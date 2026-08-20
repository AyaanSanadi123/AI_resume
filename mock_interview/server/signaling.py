# mock_interview/server/signaling.py

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.transports.base_transport import TransportParams

# Import our services and session management
from mock_interview.core.vad import InterviewVAD
from mock_interview.services.stt_service import InterviewSTTProvider
from mock_interview.services.llm_services import InterviewLLMProvider
from mock_interview.services.tts_service import InterviewTTSProvider
from mock_interview.core.pipeline import run_interview_pipeline
from mock_interview.server.session_manager import session_manager 

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

        # 1. Initialize Pipecat Transport configured for bidirectional audio streams
        transport = SmallWebRTCTransport(
            params=TransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                camera_out_enabled=False,
                mic_out_enabled=False
            )
        )

        # 2. Instantiate real-time microservices
        stt_service = InterviewSTTProvider.get_service()
        tts_service = InterviewTTSProvider.get_service()
        vad_analyzer = InterviewVAD.get_vad()

        # 3. Pull dynamic session metadata stored during session creation
        target_role = session.get("target_role", "Software Engineer")
        cache_name = session.get("cache_name")
        parsed_resume = session.get("parsed_resume", {})
        github_context = session.get("github_context", "")

        # 4. Bind LLM service utilizing the dynamic session properties and cache reference
        llm_service = InterviewLLMProvider.get_service(
            parsed_resume=parsed_resume,
            github_context=github_context,
            target_role=target_role,
            cache_name=cache_name
        )

        # 5. Handle incoming WebRTC SDP offer exchange via aiortc engine wrapper
        answer = await transport.handle_offer({"sdp": body.sdp, "type": body.type})

        # 6. Spawn background pipeline task and link it to the session tracker
        import asyncio
        task = asyncio.create_task(
            run_interview_pipeline(transport, stt_service, llm_service, tts_service, vad_analyzer)
        )
        session_manager.set_pipeline_task(session_id, task)
        session_manager.update_status(session_id, "ACTIVE")

        # 7. Return the WebRTC SDP Answer back to the Next.js client
        return JSONResponse({"sdp": answer["sdp"], "type": answer["type"]})

    except Exception as e:
        print(f"❌ Critical WebRTC Signaling Error: {e}")
        session_manager.terminate_session(session_id)
        raise HTTPException(status_code=500, detail=str(e))