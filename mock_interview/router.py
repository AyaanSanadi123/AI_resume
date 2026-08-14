'''
this acts like a all inclusive main file just for the mock-interview,
the point of this file is to not over crowded the actual main file...
'''

import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from google import genai
from dotenv import load_dotenv
from google.genai import types

from mock_interview.server.signaling import router as signaling_router
from mock_interview.server.session_manager import session_manager
from mock_interview.core.context_builder import build_interview_context

from ATS.text_extraction import TextExtraction
from ATS.resume_parser import ResumeParser

load_dotenv()

interview_router = APIRouter()
interview_router.include_router(signaling_router)


@interview_router.post("/api/interview/init", tags=["Interview Session Management"])
async def initialize_interview_session(user_id: str = Form(...),
    target_role: str = Form("AI/ML Engineer"),
    github_link: Optional[str] = Form(""),
    resume: UploadFile = File(...)):
    temp_path = None
    try:
        print(f"🚀 Initializing session for User: {user_id} | Role: {target_role}")
        extractor = TextExtraction(resume)
        raw_text,sections = extractor.process()

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY is missing from environment variables.")

        parser = ResumeParser(api_key=api_key)
        parsed_resume = parser.parse(raw_text=raw_text, sections=sections)


        github_context_placeholder = f"GitHub Profile Provided: {github_link}" if github_link else "No GitHub link provided."


        formatted_context = build_interview_context(
            parsed_resume=parsed_resume,
            github_context=github_context_placeholder,
            target_role=target_role
        )

        cache_name = None
        try:
            client = genai.Client(api_key=api_key)
            # Create a cached context using Gemini caching API
            cache = client.caches.create(
                model="gemini-3.5-flash",
                config=types.CreateCachedContentConfig(
                    contents=[formatted_context],
                    ttl="300s", # 5 minutes TTL per interview session room
                )
            )
            cache_name = cache.name
            print(f"🧠 Successfully created Gemini Context Cache: {cache_name}")
        except Exception as cache_error:
            print(f"⚠️ Warning: Failed to create Gemini cache, falling back to direct context: {cache_error}")

        session_id = session_manager.create_session(user_id=user_id, cache_name=cache_name)

        session = session_manager.get_session(session_id)
        if session:
            session["target_role"] = target_role
            session["parsed_resume"] = parsed_resume
            session["github_context"] = formatted_context
            session_manager.update_status(session_id, "READY")

        return {
            "success": True,
            "session_id": session_id,
            "message": "Interview session initialized successfully with ATS parsing and context caching.",
            "candidate_name": parsed_resume.get("name", "Candidate")
        }

    except Exception as e:
        print(f"❌ Failed to initialize interview session: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))