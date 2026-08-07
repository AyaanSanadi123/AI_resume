import os
from google import genai
from google.genai import types
from adaptive_interview.models.interview_question import QuestionBank

class InterviewGenerator:
    """Interfaces with Gemini to generate the interview question bank using google.genai SDK."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash"

    def generate(self, prompt: str) -> QuestionBank:
        """
        Sends the structured prompt to Gemini and returns a QuestionBank object.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=QuestionBank
                )
            )
            return QuestionBank.model_validate_json(response.text)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate interview questions: {str(e)}")
