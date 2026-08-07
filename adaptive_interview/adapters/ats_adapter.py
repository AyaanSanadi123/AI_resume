import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any
from google import genai
from google.genai import types

from adaptive_interview.models.resume_profile import ResumeProfile
from adaptive_interview.models.ats_analysis import ATSAnalysis

class ATSProvider(ABC):
    @abstractmethod
    def generate_ats_analysis(self, profile: ResumeProfile, job_description: str) -> ATSAnalysis:
        pass

class TemporaryATSProvider(ATSProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash" # Use current supported model

    def generate_ats_analysis(self, profile: ResumeProfile, job_description: str) -> ATSAnalysis:
        prompt = f"""You are an Applicant Tracking System.
Evaluate the candidate's resume against this Job Description.

Candidate Resume Profile:
{profile.model_dump_json(indent=2)}

Job Description:
{job_description}

Return ATS Score, Keyword Similarity, Semantic Similarity, Matched Skills, Missing Skills, Missing Competencies, Strengths, Weaknesses, and Reasoning.
Return JSON only matching the schema exactly.
"""
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ATSAnalysis
            )
        )
        
        try:
            return ATSAnalysis.model_validate_json(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to parse ATSAnalysis from Gemini response: {e}\nResponse: {response.text}")
