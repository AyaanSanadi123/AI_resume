import os
import json
from pathlib import Path
from statistics import stdev
from typing import List, Dict, Any, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# -------------------------------------------------------------
# 1. Pydantic Schemas for the Master Scorecard
# -------------------------------------------------------------
class PillarScore(BaseModel):
    score: int = Field(description="A numerical score from 0 to 100.")
    status: Literal["Good", "Average", "Bad"] = Field(description="Strict categorical status.")
    feedback: str = Field(description="1-2 sentences of clear, actionable feedback speaking directly to the candidate.")

class ActionPlan(BaseModel):
    needs_reformatting: bool = Field(description="True if Structural Health score is below 70.")
    needs_metric_injection: bool = Field(description="True if Metric Density score is below 70.")
    needs_vocabulary_upgrade: bool = Field(description="True if Linguistic Vigor or Semantic Depth score is below 70.")

class ResumeScorecard(BaseModel):
    # The 5 Pillars
    structural_health: PillarScore = Field(description="The pre-calculated structural layout score passed directly into the prompt.")
    metric_density: PillarScore = Field(description="Evaluates presence of business impact, numbers, and scale metrics.")
    linguistic_vigor: PillarScore = Field(description="Evaluates strong action verbs and absence of passive fluff.")
    semantic_depth: PillarScore = Field(description="Evaluates if claimed skills are demonstrated in the project/experience bullets.")
    readability: PillarScore = Field(description="Evaluates bullet point conciseness, pacing, and scannability.")
    
    # Holistic Summary & Action Trigger
    executive_verdict: str = Field(description="A 2-3 sentence overall summary written in an encouraging, supportive career-coach tone.")
    action_plan: ActionPlan = Field(description="Boolean flags to trigger specific 'Improve My Resume' UI checkboxes.")

# -------------------------------------------------------------
# 2. The Resume Auditor Engine
# -------------------------------------------------------------
class ResumeAuditor:
    def __init__(self):
        print("🔍 Booting up Diagnostic Resume Auditor...")
        
        # Safely locate and load .env
        parent_env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(dotenv_path=parent_env_path)
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ Error: GEMINI_API_KEY could not be found.")
            
        self.client = genai.Client(api_key=api_key)

    def calculate_structural_health(self, raw_sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Pure Python Deterministic Check:
        Calculates the standard deviation of x0 coordinates to detect multi-column layout issues.
        """
        x0_list = []
        
        for item in raw_sections:
            if isinstance(item, dict) and "x0" in item and item.get("class") != "section-header":
                x0_list.append(item["x0"])

        # Edge-case handling: If insufficient blocks extracted
        if len(x0_list) < 2:
            return {
                "score": 85,
                "status": "Good",
                "feedback": "Standard document layout detected with consistent margins."
            }

        # Calculate standard deviation of starting horizontal positions
        alignment_variance = stdev(x0_list)
        print(alignment_variance,"\n")

        if alignment_variance < 40:
            return {
                "score": 90,
                "status": "Good",
                "feedback": "Your resume uses a clean, single-column layout that ATS parsers can easily read."
            }
        elif alignment_variance <= 80:
            return {
                "score": 70,
                "status": "Average",
                "feedback": "Your layout has moderate indentation variance or aligned dates, but remains mostly readable."
            }
        else:
            return {
                "score": 40,
                "status": "Bad",
                "feedback": "Multiple columns or complex formatting detected. Older ATS engines will likely scramble this text."
            }

    def audit_resume(self, parsed_resume_json: Dict[str, Any], raw_sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        # Step 1: Pre-calculate Structural Health via Python math
        structural_result = self.calculate_structural_health(raw_sections)

        # Step 2: Formulate the single-pass prompt
        prompt = f"""
        You are an elite AI Career Coach and Senior Technical Recruiter.
        Your job is to audit the provided candidate resume JSON and return a comprehensive diagnostic scorecard.

        --- PRE-CALCULATED DATA (DO NOT OVERWRITE) ---
        The structural layout health of this resume has already been mathematically evaluated by the system:
        Score: {structural_result['score']}
        Status: {structural_result['status']}
        Feedback: {structural_result['feedback']}

        You MUST pass these exact values directly into the `structural_health` object of your JSON output.

        --- YOUR EVALUATION INSTRUCTIONS ---
        Evaluate the remaining 4 pillars using the candidate's parsed resume JSON:
        1. Metric Density: Assess if bullet points quantify business impact (numbers, %, scale, latency) versus listing passive duties.
        2. Linguistic Vigor: Check for strong, active verbs ("Architected", "Engineered") instead of passive phrases ("Worked on", "Responsible for").
        3. Semantic Depth: Cross-reference the `skills` array against `projects` and `experience`. Flag skills that are listed but never mentioned in descriptions.
        4. Readability: Evaluate bullet length, information density, and scannability.

        SYNTHESIS REQUIREMENTS:
        - Write an `executive_verdict` (2-3 sentences) in an encouraging, constructive career-coach tone summarizing what is strong and what needs improvement.
        - Populate `action_plan` booleans (`true` if the respective score is below 70, `false` otherwise).

        --- PARSED RESUME JSON ---
        {json.dumps(parsed_resume_json, indent=2)}
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ResumeScorecard,
                    temperature=0.2, # Low temperature for accurate, consistent evaluation
                ),
            )
            
            return response.parsed.model_dump()

        except Exception as e:
            print(f"🔥 Audit Exception caught: {str(e)}")
            return {"error": f"Failed to generate audit scorecard: {str(e)}"}

