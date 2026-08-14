'''
this acts like a all inclusive main file just for the mock-interview,
the point of this file is to not over crowded the actual main file...
'''

import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from google import genai
from dotenv import load_dotenv

from mock_interview.server.signaling import router as signaling_router
from mock_interview.server.session_manager import session_manager
from mock_interview.core.context_builder import build_interview_context

from ATS.text_extraction import TextExtraction
from ATS.resume_parser import ResumeParser

load_dotenv()

interview_router = APIRouter()
interview_router.include_router(signaling_router)
