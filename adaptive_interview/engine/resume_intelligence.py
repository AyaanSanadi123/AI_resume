import os
from google import genai
from google.genai import types
from adaptive_interview.models.resume_profile import ResumeProfile
from adaptive_interview.models.ats_analysis import ATSAnalysis
from adaptive_interview.models.interview_signal import InterviewSignal

class ResumeIntelligenceEngine:
    """Uses Gemini to perform semantic reasoning over the ResumeProfile and ATSAnalysis, returning an InterviewSignal."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash"

    def analyze(self, profile: ResumeProfile, ats_analysis: ATSAnalysis) -> InterviewSignal:
        prompt = f"""You are an expert technical engineering manager.
Analyze the candidate's Resume Profile and the ATS Analysis.
Infer what the candidate actually knows, what they have demonstrated through their projects, and what still needs to be verified.
Look for implicit competencies. For example, if they used Docker, they likely know Containerization.
Do not evaluate resume formatting or grammar. Focus entirely on technical capabilities and semantic understanding.

Resume Profile:
{profile.model_dump_json(indent=2)}

ATS Analysis:
{ats_analysis.model_dump_json(indent=2)}

Return JSON only, matching the exact schema provided. Do not generate interview questions.
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InterviewSignal
            )
        )
        try:
            return InterviewSignal.model_validate_json(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to parse InterviewSignal from Gemini response: {e}\nResponse: {response.text}")
