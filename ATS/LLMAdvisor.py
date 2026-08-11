import os
import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from typing import Dict, Any

# Automatically find and load the .env file from the directory above
parent_env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=parent_env_path)

# Define the strict output schema using Pydantic
class ResumeAdviceSchema(BaseModel):
    reality_check: str = Field(description="A blunt 1-sentence assessment of their current match.")
    skill_advice: str = Field(description="Actionable advice on closing skill gaps.")
    impact_advice: str = Field(description="Actionable advice on adding quantifiable metrics.")
    trajectory_advice: str = Field(description="Actionable advice on reframing experience/summary.")

class LLMAdvisor:
    def __init__(self):
        print("🤖 Booting up LLM Advisory Layer...")
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                f"❌ Error: GEMINI_API_KEY could not be found. "
                f"Checked environment and .env path: {parent_env_path}"
            )
            
        self.client = genai.Client(api_key=api_key)

    def _build_context_payload(self, resume_json: Dict, job_json: Dict, match_results: Dict) -> Dict:
        return {
            "candidate": {
                "title_summary": resume_json.get("summary", ""),
                "skills": resume_json.get("skills", []),
                "experience": resume_json.get("experience", []),
                "projects": resume_json.get("projects", []),
                "education": resume_json.get("education", [])
            },
            "target_job": {
                "Title": job_json.get("Title", ""),
                "ExperienceLevel": job_json.get("ExperienceLevel", ""),
                "Required_Skills": job_json.get("Skills", []),
                "Responsibilities": job_json.get("Responsibilities", [])
            },
            "engine_metrics": {
                "match_score": match_results.get("match_score"),
                "matched_skills": match_results.get("matched_skills", []),
                "missing_skills": match_results.get("missing_skills", [])
            }
        }

    def generate_advice(self, resume_json: Dict, job_json: Dict, match_results: Dict) -> Dict:
        context_payload = self._build_context_payload(resume_json, job_json, match_results)
        
        prompt = f"""
        You are an elite, no-nonsense Technical Recruiter and Career Coach. 
        Your goal is to provide radically candid, highly actionable advice to help a candidate upgrade their resume for a specific target role.

        --- INPUT DATA ---
        {json.dumps(context_payload, indent=2)}
        -----------------

        --- YOUR INSTRUCTIONS ---
        Analyze the input data and generate highly specific, actionable advice on how the candidate can improve their resume. 

        1. TONE: Be honest, direct, and realistic. Do not use corporate fluff. Be constructive but firm.
        2. TRAJECTORY ANALYSIS (Pivot vs. Climber): Compare the candidate's current experience level against the Target Job's "ExperienceLevel". 
           - "Climber" (jumping in seniority): Advise on demonstrating scale, leadership, and architecture.
           - "Pivot" (changing domains): Advise on reframing existing projects to highlight transferable skills.
        3. THE THREE GAPS:
           - "skill_advice": Tell them how to acquire or demonstrate the highest-priority missing skills by modifying an existing project on their resume or building a specific new one.
           - "impact_advice": Identify a specific project or experience in their resume that lacks quantifiable metrics. Tell them exactly what kind of numbers to add.
           - "trajectory_advice": Advise them on how to reframe their summary or narrative for this role's level and domain.
        """

        try:
            # Enforce strict parsing through Pydantic schema validation
            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ResumeAdviceSchema,
                ),
            )
            
            # response.text is guaranteed to match the Pydantic JSON layout safely
            return json.loads(response.text)
            
        except Exception as e:
            print(f"🔥 LLM API Exception caught: {str(e)}")
            return {"error": f"Failed to generate advice: {str(e)}"}