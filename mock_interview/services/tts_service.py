
import os
from dotenv import load_dotenv
from pipecat.services.deepgram.tts import DeepgramTTSService

load_dotenv()

class InterviewTTSProvider:
    """
    Initializes and configures Deepgram Aura Text-to-Speech service 
    utilizing your shared Deepgram developer credits.
    """
    
    @staticmethod
    def get_service() -> DeepgramTTSService:
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise ValueError("❌ Missing DEEPGRAM_API_KEY in .env file.")

        print("🔊 Initializing Deepgram Aura TTS Service...")
        
        return DeepgramTTSService(
            api_key=api_key,
            # 'aura-asteria-en' or 'aura-luna-en' are great natural-sounding professional voices
            model="aura-luna-en", 
            sample_rate=16000, # Matches WebRTC standard
        )