# mock_interview/server/signaling.py

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.transports.base_transport import TransportParams

# ---> FIX: Use Pipecat's specialized wrapper instead of raw aiortc
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection 

# Import our services and session management
from mock_interview.core.vad import InterviewVAD
from mock_interview.services.stt_service import InterviewSTTProvider
from mock_interview.services.llm_services import InterviewLLMProvider
from mock_interview.services.tts_service import InterviewTTSProvider
from mock_interview.core.pipeline import run_interview_pipeline
from mock_interview.server.session_manager import session_manager 
import asyncio

router = APIRouter(prefix="/api/interview", tags=["Interview WebRTC Signaling"])

class OfferRequest(BaseModel):
    session_id: str
    sdp: str
    type: str

@router.post("/offer")
async def handle_webrtc_offer(request: Request, body: OfferRequest):

    session_id = body.session_id
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found, expired, or uninitialized.")

    try:
        print(f"📡 Processing production WebRTC Offer for session: {session_id}")

        # 1. Initialize Pipecat's specialized WebRTC Connection
        pc = SmallWebRTCConnection()

        # 2. Handle incoming WebRTC SDP offer directly on the connection
        await pc.initialize(sdp=body.sdp, type=body.type)
        answer = pc.get_answer()

        if not answer:
            raise Exception("Failed to generate WebRTC answer.")

        # 3. Inject it into Pipecat Transport
        transport = SmallWebRTCTransport(
            webrtc_connection=pc,
            params=TransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                camera_out_enabled=False,
                mic_out_enabled=False
            )
        )

        # 4. Instantiate real-time microservices
        stt_service = InterviewSTTProvider.get_service()
        tts_service = InterviewTTSProvider.get_service()
        vad_analyzer = InterviewVAD.get_vad()

        # 5. Pull dynamic session metadata stored during session creation
        target_role = session.get("target_role", "Software Engineer")
        cache_name = session.get("cache_name")
        parsed_resume = session.get("parsed_resume", {})
        github_context = session.get("github_context", "")

        # 6. Bind LLM service utilizing the dynamic session properties and cache reference
        llm_service = InterviewLLMProvider.get_service(
            parsed_resume=parsed_resume,
            github_context=github_context,
            target_role=target_role,
            
        )

        # 7. Spawn background pipeline task and link it to the session tracker
        task = asyncio.create_task(
            run_interview_pipeline(transport, stt_service, llm_service, tts_service, vad_analyzer)
        )
        session_manager.set_pipeline_task(session_id, task)
        session_manager.update_status(session_id, "ACTIVE")

        # 8. Return the WebRTC SDP Answer back to the Next.js client
        return JSONResponse(answer)

    except Exception as e:
        print(f"❌ Critical WebRTC Signaling Error: {e}")
        session_manager.terminate_session(session_id)
        raise HTTPException(status_code=500, detail=str(e))