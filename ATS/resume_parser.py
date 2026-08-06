import re
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()
load_dotenv(dotenv_path="../.env")

# -------------------------------------------------------------
# 1. Edge-Case Resilient Pydantic Schemas
# -------------------------------------------------------------
class ExperienceModel(BaseModel):
    company: Optional[str] = Field(description="Name of the company, organization, or freelance client. If missing, use 'Independent' or null.")
    title: Optional[str] = Field(description="Job title, role designation, or position held.")
    dates: Optional[str] = Field(description="Employment timeline or duration (e.g., Jan 2026 – Present). Keep null if not specified.")
    bullets: List[str] = Field(description="List of responsibilities, achievements, metrics, or duties performed.")

class ProjectModel(BaseModel):
    name: Optional[str] = Field(description="Name of the project, system, or software build.")
    dates: Optional[str] = Field(description="Timeline or period of the project if available.")
    bullets: List[str] = Field(description="Technical architecture, tools used, key features, or impact.")

class EducationModel(BaseModel):
    institution: Optional[str] = Field(description="Name of the university, college, or high school institution.")
    degree: Optional[str] = Field(description="Degree name, major, diploma, or field of study (including CGPA/GPA if present).")
    dates: Optional[str] = Field(description="Graduation year, timeline, or expected completion date.")

class CertificationModel(BaseModel):
    name: Optional[str] = Field(description="Name of the certification, license, or credential.")
    issuer: Optional[str] = Field(description="Issuing organization or platform (e.g., AWS, Google, Coursera, HackerRank).")
    date: Optional[str] = Field(description="Date obtained or expiration date if specified.")

class ResumeSchema(BaseModel):
    name: Optional[str] = Field(description="The full name of the candidate extracted from the header.")
    summary: Optional[str] = Field(description="The professional summary, objective, profile, or 'About Me' text block.")
    skills: List[str] = Field(description="List of technical skills, frameworks, tools, programming languages, and soft skills.")
    experience: List[ExperienceModel] = Field(description="Professional work experience, corporate internships, or formal employment ONLY. Treat remote or freelance contracts here if they have a company/client name.")
    projects: List[ProjectModel] = Field(description="Independent, academic, or personal software builds and engineering projects. Look for headers like 'Projects', 'Key Works', 'Personal Projects', or 'Academic Builds'.")
    education: List[EducationModel] = Field(description="Formal degrees, schools, and academic background.")
    certifications: List[CertificationModel] = Field(description="Professional certifications, industry credentials, or licenses.")
    awards_and_honors: List[str] = Field(description="List of awards, hackathon wins, competitive coding ranks, or honors.")

# -------------------------------------------------------------
# 2. The Hybrid Parser
# -------------------------------------------------------------
class ResumeParser:
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
        self.client = genai.Client(api_key=key)
        
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}')
        self.link_pattern = re.compile(r'(?:https?://)?(?:www\.)?(github\.com/[^\s]+|linkedin\.com/in/[^\s]+)')

    def _extract_entities(self, raw_text: str) -> Dict[str, List[str]]:
        emails = list(set(self.email_pattern.findall(raw_text)))
        phones = list(set(self.phone_pattern.findall(raw_text)))
        links = list(set(self.link_pattern.findall(raw_text)))

        return {
            "emails": [e.strip() for e in emails],
            "phones": [p.strip() for p in phones],
            "links": [l.strip() for l in links]
        }

    def _sort_spatially(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(sections, key=lambda b: (round(b.get('y0', 0) / 15), b.get('x0', 0)))

    def parse(self, raw_text: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        hard_contacts = self._extract_entities(raw_text)
        sorted_blocks = self._sort_spatially(sections)
        
        layout_text = ""
        for block in sorted_blocks:
            x = block.get('x0', 0)
            y = block.get('y0', 0)
            text = block.get('text', '')
            layout_text += f"[x: {x:.1f}, y: {y:.1f}] {text}\n"

        prompt = f"""
        You are an expert resume parsing engine. I am providing you with text blocks extracted from a resume along with their spatial coordinates [x, y].
        
        CRITICAL PARSING RULES:
        1. **Layout Integrity:** Use coordinates to keep independent columns separated and avoid cross-contaminating sidebars with main body sections.
        2. **Experience vs. Projects:** 
           - 'experience' is strictly for formal employment, internships, or professional client work.
           - 'projects' is strictly for personal, open-source, or academic software engineering builds. Do not mix them up.
        3. **Edge Case Handling:**
           - If a field like 'dates' or 'company' is missing, leave it as `null` rather than hallucinating values.
           - Capture professional licenses or online credentials under 'certifications'.
           - Capture competitive achievements or hackathon wins under 'awards_and_honors'.
        4. **Normalization:** Ignore minor OCR spacing anomalies, header typos, or non-standard naming conventions for sections (e.g., treat "Key Endeavors" or "Academic Works" appropriately).
        
        RESUME DATA STREAM:
        {layout_text}
        """

        response = self.client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeSchema,
                temperature=0.0,
            ),
        )

        final_json = response.parsed.model_dump()
        final_json["contact_info"] = hard_contacts

        return final_json