
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pipecat.services.google import GoogleLLMService

load_dotenv()

class InterviewLLMProvider:
    
    def get_service(parsed_resume: dict, github_context: str, target_role: str) -> GoogleLLMService:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ Missing GEMINI_API_KEY in .env file.")

        print(f"🧠 Setting up Context Cache & Gemini Brain for {target_role}...")

        # 1. Initialize the official Google GenAI client for cache creation
        client = genai.Client(api_key=api_key)

        # 2. Build the static background data we want to cache
        system_instruction = f"""
        You are an elite, rigorous technical interviewer conducting a mock interview for a {target_role} position.
        Your goal is to test the candidate strictly on their actual background, code, and project architecture. 
        Ask one specific question at a time, wait for the response, and dig deep into their technical choices.
        """

        candidate_corpus = f"""
        --- CANDIDATE RESUME DATA ---
        {parsed_resume}
        
        --- CANDIDATE GITHUB & CODE CONTEXT ---
        {github_context}
        """

        # 3. Create the explicit cache on Google's servers (Expires in 30 minutes)
        # Note: Gemini caching requires a minimum token limit (usually 2048+ tokens). 
        # If your resume/GitHub context is small, Gemini handles it via implicit caching automatically.
        try:
            cache = client.caches.create(
                model="models/gemini-3.5-flash",
                config=types.CreateCachedContentConfig(
                    model="models/gemini-3.5-flash",
                    system_instruction=system_instruction,
                    contents=[candidate_corpus],
                    ttl="1800s", # 30 minute time-to-live
                ),
            )
            cache_name = cache.name
            print(f"✅ Context Cache successfully created! ID: {cache_name}")
        except Exception as e:
            print(f"⚠️ Warning: Could not create explicit cache (context might be under token minimum). Falling back to standard prompt: {e}")
            cache_name = None

        # 4. Configure Pipecat's GoogleLLMService
        # If cache was successfully created, we pass it via the 'extra' settings parameter
        extra_config = {"cached_content": cache_name} if cache_name else {}

        return GoogleLLMService(
            api_key=api_key,
            settings=GoogleLLMService.Settings(
                model="gemini-3.5-flash",
                system_instruction=system_instruction if not cache_name else None, # Handled by cache if active
                temperature=0.7,
                extra=extra_config
            )
        )