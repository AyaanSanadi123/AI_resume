'''
this acts as a source of truth during the life cycle of an interview,
INITIALIZING, ACTIVE, COMPLETED, 
maps user IDs to active session tokens, and ensures background resources,
get wiped out when an interview terminates so you don't leak memory or rack up storage charges.
'''

"""
DESIGN 
this must contain 3 major compoenents 
1. session state data structure -> this will map the unique session_id with 
user_id, status, cache_name, pipeline_task and start_time

"""

import os
import uuid
import time
from typing import Dict, Any, Optional
from google import genai
from dotenv import load_dotenv

load_dotenv()

class SessionManager:
    def __init__(self):
        self.__sessions : Dict[str,Dict[str,Any]] = {} # {session_id : {meta_data}}

    def create_session(self,user_id : str, cache_name : Optional[str] = None)-> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "status": "INITIALIZING",
            "cache_name": cache_name,
            "pipeline_task": None,
            "start_time": time.time()
        }
        print(f"📁 Session Created: {session_id} for User: {user_id}")
        return session_id

    def set_pipeline_task(self, session_id: str, task: Any):
        
        if session_id in self._sessions:
            self._sessions[session_id]["pipeline_task"] = task

    def update_status(self, session_id: str, status: str):
        if session_id in self._sessions:
            self._sessions[session_id]["status"] = status
            print(f"🔄 Session {session_id} status updated to: {status}")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        
        return self._sessions.get(session_id)

    
    def terminate_session(self, session_id: str):
        
        session = self._sessions.get(session_id)
        if session:
            print(f"🛑 Terminating session: {session_id}...")
            
            # 1. Cancel active Pipecat background task if running
            task = session.get("pipeline_task")
            if task:
                try:
                    task.cancel()
                except Exception as e:
                    print(f"⚠️ Error canceling pipeline task: {e}")
            
            # 2. Trigger Google GenAI cache deletion to clear server storage
            cache_name = session.get("cache_name")
            if cache_name and self._genai_client:
                try:
                    self._genai_client.caches.delete(name=cache_name)
                    print(f"🗑️ Successfully deleted Gemini Context Cache: {cache_name}")
                except Exception as e:
                    print(f"⚠️ Failed to delete Gemini cache ({cache_name}): {e}")

            # 3. Remove from active store
            del self._sessions[session_id]
            print(f"🧹 Session {session_id} successfully wiped from memory.")


session_manager = SessionManager()