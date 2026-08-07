import os
from google import genai
from google.genai import types
from adaptive_interview.models.role_profile import RoleProfile

class RoleUnderstandingEngine:
    """Uses Gemini to parse the Job Description and return a structured RoleProfile."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash"

    def analyze(self, job_description: str) -> RoleProfile:
        prompt = f"""You are an expert technical recruiter and engineering manager.
Analyze the following Job Description and extract the key information into a structured role profile.
Identify implicit requirements that are not explicitly listed (e.g. if YOLO is mentioned, infer Computer Vision, CNNs). Include these in related_concepts.
Assign priority weights (0.0 to 1.0) to skills based on how heavily they are emphasized in the description.

Job Description:
{job_description}

Return JSON only, matching the exact schema provided.
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RoleProfile
            )
        )
        try:
            return RoleProfile.model_validate_json(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to parse RoleProfile from Gemini response: {e}\nResponse: {response.text}")
