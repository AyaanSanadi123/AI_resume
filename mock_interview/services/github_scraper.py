# mock_interview/services/github_scraper.py

import os
import re
import httpx
from typing import Optional

class GitHubScraper:
    """
    Scrapes a candidate's public GitHub profile and repositories via public URL, 
    cleans the noise, includes topics, and outputs a token-optimized Markdown summary.
    """
    
    def __init__(self, github_url: str):
        self.username = self._extract_username(github_url)
        # Unauthenticated headers (GitHub allows public requests up to 60/hr per IP)
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Mock-Interview-Engine"
        }

    def _extract_username(self, url: str) -> Optional[str]:
        """Extracts the github username from various URL formats (e.g., https://github.com/username)."""
        if not url:
            return None
        clean_url = url.strip().rstrip("/")
        parts = clean_url.split("/")
        return parts[-1] if parts else None

    def _clean_readme_text(self, raw_readme: str) -> str:
        """
        Aggressively strips noise from README text to preserve tokens:
        - Removes HTML tags, badges, and image links.
        - Removes massive code blocks or installation boilerplates.
        - Truncates length up to 1000 characters to keep context rich yet lean.
        """
        if not raw_readme:
            return "No README available."

        # 1. Strip markdown images and badges: [![Build...](url)](url) or ![alt](url)
        text = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', raw_readme)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        
        # 2. Strip HTML tags (<br>, <div>, etc.)
        text = re.sub(r'<[^>]*>', '', text)
        
        # 3. Strip massive code blocks (``` ... ```) to save structural noise
        text = re.sub(r'```[\s\S]*?```', '[Code Snippet Omitted]', text)

        # 4. Normalize whitespace and newlines
        text = " ".join(text.split())

        # 5. Limit length up to 1000 characters for rich contextual depth without token waste
        if len(text) > 1000:
            text = text[:1000] + "..."

        return text

    async def scrape_and_clean(self) -> str:
        """
        Master method: Fetches public repositories, extracts metadata, topics, 
        and cleaned READMEs up to 1000 characters into a minimal Markdown string.
        """
        if not self.username:
            return "No valid GitHub username provided."

        print(f"🔍 Scraping and cleaning public GitHub data for user: {self.username}...")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # 1. Fetch user public repositories (sorted by last updated, limit to top 5)
                repos_url = f"https://api.github.com/users/{self.username}/repos?sort=updated&per_page=5"
                response = await client.get(repos_url, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"⚠️ GitHub API Error: Status {response.status_code}")
                    return f"Failed to fetch public GitHub profile for {self.username} (Rate limit or invalid user)."

                repos = response.json()
                if not isinstance(repos, list) or not repos:
                    return f"No public repositories found for {self.username}."

                cleaned_markdown_lines = [f"=== GITHUB REPOSITORY ANALYSIS ({self.username}) ==="]

                for repo in repos:
                    # Filter out forks to focus purely on original candidate builds
                    if repo.get("fork", False):
                        continue

                    name = repo.get("name", "Unknown Repo")
                    description = repo.get("description", "No description provided.")
                    language = repo.get("language", "Not Specified")
                    stars = repo.get("stargazers_count", 0)
                    
                    # Extract repository topics/tags
                    topics = repo.get("topics", [])
                    topics_str = ", ".join(topics) if topics else "None specified"

                    # 2. Attempt to fetch README for deeper technical context
                    readme_summary = "No README."
                    try:
                        readme_url = f"https://api.github.com/repos/{self.username}/{name}/readme"
                        readme_res = await client.get(readme_url, headers=self.headers)
                        if readme_res.status_code == 200:
                            import base64
                            content_encoded = readme_res.json().get("content", "")
                            decoded_bytes = base64.b64decode(content_encoded)
                            raw_readme = decoded_bytes.decode("utf-8", errors="ignore")
                            
                            # Apply our strict cleaning logic with expanded 1000-char limit
                            readme_summary = self._clean_readme_text(raw_readme)
                    except Exception:
                        pass # Non-fatal if README fetch fails

                    # 3. Compress into tight Markdown format including repo names and topics
                    cleaned_markdown_lines.append(
                        f"- **Repository Name:** {name}\n"
                        f"  - **Language:** {language} | **Stars:** {stars} | **Topics:** {topics_str}\n"
                        f"  - **Description:** {description}\n"
                        f"  - **Architecture / Notes:** {readme_summary}"
                    )

                return "\n".join(cleaned_markdown_lines)

            except Exception as e:
                print(f"❌ GitHub Scraper Exception: {e}")
                return f"Error analyzing GitHub activity for {self.username}."