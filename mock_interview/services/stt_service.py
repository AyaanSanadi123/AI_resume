'''
speech to text 
'''

import os
from dotenv import load_dotenv
from pipecat.services.deepgram import DeepgramSTTService

load_dotenv()

class InterviewSTTProvider:

    def get_service() -> DeepgramSTTService:
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise ValueError("❌ Missing DEEPGRAM_API_KEY in .env file.")

        print("🎙️ Initializing Deepgram STT Service...")
        
        return DeepgramSTTService(
            api_key=api_key,
            # 'nova-2' is Deepgram's most accurate and fastest model for voice AI
            model="nova-2", 
            language="en",
            # WebRTC standard audio settings
            sample_rate=16000,
            channels=1,
        )