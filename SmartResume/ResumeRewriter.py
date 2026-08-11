import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 1. Pydantic Schemas (Must exactly match the original structure)
# -------------------------------------------------------------
class ExperienceModel(BaseModel):
    company: Optional[str] = Field(description="Name of the company, organization, or freelance client.")
    title: Optional[str] = Field(description="Job title, role designation, or position held.")
    dates: Optional[str] = Field(description="Employment timeline or duration.")
    bullets: List[str] = Field(description="List of rewritten responsibilities and achievements.")

class ProjectModel(BaseModel):
    name: Optional[str] = Field(description="Name of the project, system, or software build.")
    dates: Optional[str] = Field(description="Timeline or period of the project if available.")
    bullets: List[str] = Field(description="List of rewritten technical architecture, tools used, and impact.")

class EducationModel(BaseModel):
    institution: Optional[str] = Field(description="Name of the university, college, or high school institution.")
    degree: Optional[str] = Field(description="Degree name, major, diploma, or field of study.")
    dates: Optional[str] = Field(description="Graduation year, timeline, or expected completion date.")

class CertificationModel(BaseModel):
    name: Optional[str] = Field(description="Name of the certification, license, or credential.")
    issuer: Optional[str] = Field(description="Issuing organization or platform.")
    date: Optional[str] = Field(description="Date obtained or expiration date if specified.")

class ContactInfoModel(BaseModel):
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)

class EnhancedResumeSchema(BaseModel):
    name: Optional[str] = Field(description="The full name of the candidate. Keep exactly as provided.")
    summary: Optional[str] = Field(description="The rewritten professional summary.")
    skills: List[str] = Field(description="List of technical skills. Keep exactly as provided or standardize names.")
    experience: List[ExperienceModel] = Field(description="Rewritten professional work experience.")
    projects: List[ProjectModel] = Field(description="Rewritten independent and academic projects.")
    education: List[EducationModel] = Field(description="Academic background. Keep exactly as provided.")
    certifications: List[CertificationModel] = Field(description="Professional certifications. Keep exactly as provided.")
    awards_and_honors: List[str] = Field(description="List of awards. Keep exactly as provided.")
    contact_info: ContactInfoModel = Field(description="Contact details. Keep exactly as provided.")

# -------------------------------------------------------------
# 2. The Auto-Rewriter Engine
# -------------------------------------------------------------
class ResumeRewriter:
    def __init__(self):
        print("🪄 Booting up LLM Auto-Rewriter Layer...")
        
        # Safely find and load .env
        parent_env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(dotenv_path=parent_env_path)
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(f"❌ Error: GEMINI_API_KEY could not be found.")
            
        self.client = genai.Client(api_key=api_key)

    def rewrite_resume(self, parsed_resume_json: Dict[str, Any],scorecard_json:Dict[str, Any]) -> Dict[str, Any]:
       
        prompt = f"""
        You are an elite Technical Recruiter and Resume Engineer specializing in Software Engineering and AI. 
        Your objective is to rewrite the provided candidate resume JSON to maximize its impact for ATS systems and hiring managers.

        You must output a JSON object that strictly adheres to the requested schema. 
        DO NOT alter the `name`, `contact_info`, or `education` data. Focus entirely on upgrading the `experience`, `projects`, and `summary` content.

        --- DIAGNOSTIC SCORECARD CONTEXT ---
        The candidate's resume was just audited. Use this diagnostic feedback to guide your highly targeted surgical edits:
        {json.dumps(scorecard_json, indent=2)}

        --- CRITICAL REWRITE RULES ---

        1. THE STAR METHOD (Action + Context + Result)
        Rewrite every single string in the `bullets` arrays for both `experience` and `projects`. 
        Do not write passive tasks. You must write high-impact achievements.

        2. THE TARGETED BRACKET STRATEGY (Anti-Hallucination)
        You are strictly forbidden from inventing metrics. However, impact requires numbers.
        Whenever a bullet lacks a quantifiable metric, you MUST inject a bolded placeholder bracket. 
        CRITICAL: Read the `metric_density` feedback from the scorecard and create highly specific brackets based on it (e.g., **[Insert Latency Reduction in ms]** or **[Insert % Accuracy Improvement]** instead of a generic **[Insert %]**).

        3. LINGUISTIC VIGOR & JARGON (Elevate Vocabulary)
        Upgrade generic terms to industry-standard technical jargon. Ensure every bullet starts with a powerful past-tense action verb (e.g., Architected, Engineered, Quantized). Look at the `linguistic_vigor` feedback to see what verbs need upgrading.

        4. SEMANTIC INTEGRATION (Show, Don't Tell)
        Read the `semantic_depth` feedback. If the auditor identified missing technologies (e.g., MongoDB, Git, PyTorch) that are in the skills list but missing from the bullets, seamlessly and logically weave them into the rewritten project or experience descriptions. Do not leave orphaned skills.

        5. READABILITY & BREVITY
        Read the `readability` feedback. Ensure no bullet point is a massive run-on sentence. Keep them dense, scannable, and eliminate redundant fluff. Maximum 200 characters per bullet point.

        6. SUMMARY REWRITE
        Rewrite the `summary` field to be a powerful, 2-sentence executive technical profile.

        --- RAW CANDIDATE RESUME ---
        {json.dumps(parsed_resume_json, indent=2)}
        """
        
        try:
            # Generate the structured rewrite
            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EnhancedResumeSchema,
                    temperature=0.3, # Low temperature to prevent wild formatting hallucinations
                ),
            )
            
            # response.parsed contains the validated Pydantic object
            return response.parsed.model_dump()
            
        except Exception as e:
            print(f"🔥 Auto-Rewriter API Exception caught: {str(e)}")
            return {"error": f"Failed to rewrite resume: {str(e)}"}

