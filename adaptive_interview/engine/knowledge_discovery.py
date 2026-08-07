import os
from google import genai
from google.genai import types
from adaptive_interview.models.resume_profile import ResumeProfile
from adaptive_interview.models.ats_analysis import ATSAnalysis
from adaptive_interview.models.role_profile import RoleProfile
from adaptive_interview.models.knowledge_graph import KnowledgeGraph

class KnowledgeDiscoveryEngine:
    """Uses Gemini to build a structured KnowledgeGraph from Resume, ATS, and Role Profiles."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash"

    def discover(self, profile: ResumeProfile, ats_analysis: ATSAnalysis, role_profile: RoleProfile) -> KnowledgeGraph:
        prompt = f"""You are an expert technical interviewer and software architect.
Analyze the provided candidate Resume Profile, ATS Analysis, and Target Role Profile.
Build a comprehensive Knowledge Graph of technologies and concepts that should be evaluated.
Identify semantic relationships between concepts (e.g., YOLO -> Object Detection -> Computer Vision -> CNN -> Deep Learning).
Determine prerequisite concepts, related technologies, and logical follow-ups for each concept to be evaluated.

Resume Profile:
{profile.model_dump_json(indent=2)}

ATS Analysis:
{ats_analysis.model_dump_json(indent=2)}

Role Profile:
{role_profile.model_dump_json(indent=2)}

Return JSON only, matching the exact schema provided. Do not generate interview questions.
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=KnowledgeGraph
            )
        )
        try:
            return KnowledgeGraph.model_validate_json(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to parse KnowledgeGraph from Gemini response: {e}\nResponse: {response.text}")
