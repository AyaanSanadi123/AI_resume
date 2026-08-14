# mock_interview/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Centralized configuration settings for the real-time mock interview pipeline.
    """
    PROJECT_NAME: str = "Real-Time AI Mock Interview Engine"
    VERSION: str = "1.0.0"
    
    # API Keys
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Model Names & Defaults
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    DEEPGRAM_STT_MODEL: str = os.getenv("DEEPGRAM_STT_MODEL", "nova-3-general")
    DEEPGRAM_TTS_MODEL: str = os.getenv("DEEPGRAM_TTS_MODEL", "aura-luna-en")

# Global singleton configuration instance
settings = Settings()