# test_github_scraper.py

import asyncio
import os
from github_scraper import GitHubScraper

async def run_test():
    # 1. Target profile URL provided
    test_url = "https://github.com/AyaanSanadi123"
    print(f"🚀 Initializing GitHub scraper test for: {test_url}")

    # 2. Instantiate the scraper service
    scraper = GitHubScraper(test_url)

    # 3. Execute the scrape and clean pipeline
    markdown_output = await scraper.scrape_and_clean()

    # 4. Save the compressed markdown output to a file in the same directory
    output_filename = "github_analysis_output.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(markdown_output)

    print(f"✅ Success! Scraped GitHub output saved to: {os.path.abspath(output_filename)}")
    print("\n--- PREVIEW OF MARKDOWN OUTPUT ---")
    print(markdown_output[:600] + "\n[... truncated preview ...]")

if __name__ == "__main__":
    asyncio.run(run_test())