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

    def rewrite_resume(self, parsed_resume_json: Dict[str, Any]) -> Dict[str, Any]:
       
        
        prompt = f"""
        You are an elite Technical Recruiter and Resume Engineer specializing in Software Engineering and AI. 
        Your objective is to rewrite the provided candidate resume JSON to maximize its impact for ATS systems and hiring managers.

        You must output a JSON object that strictly adheres to the requested schema. 
        DO NOT alter the `name`, `contact_info`, or `education` data. Focus entirely on upgrading the content.

        --- CRITICAL REWRITE RULES ---

        1. THE STAR METHOD (Action + Metric + Result)
        Rewrite every single string in the `bullets` arrays for both `experience` and `projects`. 
        Do not write passive tasks like "Worked on X." You must write high-impact achievements: "Accomplished [X] as measured by [Y], by doing [Z]."

        2. THE BRACKET STRATEGY (Anti-Hallucination)
        You are strictly forbidden from inventing or hallucinating metrics, numbers, or scale. 
        However, impact requires numbers. Whenever a bullet point lacks a quantifiable metric, you MUST inject a bolded placeholder bracket forcing the user to provide it.
        Examples: 
        - "...reducing inference latency by **[Insert %]**..."
        - "...trained on a dataset of **[Insert Number]** images..."
        - "...achieving an accuracy of **[Insert Metric]**..."

        3. JARGON STANDARDIZATION (Elevate Vocabulary)
        Upgrade generic terms to industry-standard technical jargon based on the context.
        - Instead of "made a model smaller," use "applied post-training quantization."
        - Instead of "put the app on a server," use "containerized and deployed the inference engine."
        - Instead of "tracked faces," use "implemented live facial feature extraction and kinematic tracking."

        4. SUMMARY REWRITE
        Rewrite the `summary` field to be a powerful, 2-sentence executive technical profile. Remove all generic fluff (e.g., "hardworking team player").

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

