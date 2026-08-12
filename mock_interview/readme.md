┌────────────────────────────────────────────────────────────────────────┐
 │                      1. Ingestion & Scraping                           │
 │     • Resume JSON loader         • GitHub API Repo Scraper             │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │                      2. Context & Caching Layer                        │
 │     • System Prompt builder      • Gemini Context Cache Manager        │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │                 3. WebRTC Signaling & Auth Broker                      │
 │     • Handshake endpoints        • Ephemeral Session Token Issuance    │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │                  4. Media & VAD Processing Layer                       │
 │     • WebRTC RTP unpacker        • Silero VAD Turn Detector            │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │               5. AI Microservice Connectors (Adapters)                │
 │     • STT: Deepgram/Whisper      • LLM: Gemini 2.5 Flash               │
 │     • TTS: Cartesia/ElevenLabs   • Transcript Logger                   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
 ┌───────────────────────────────────▼────────────────────────────────────┐
 │                 6. Pipeline & Session Orchestrator                     │
 │     • Real-time Async Event Loop connecting layers 3, 4 & 5            │
 └────────────────────────────────────────────────────────────────────────┘




 D:\AI_resume\
│
├── ATS/                           # Existing ATS & SmartResume engine
│   ├── main.py
│   ├── ResumeAuditor.py
│   └── ...
│
├── mock_interview/                # New Real-Time Voice Interview Engine
│   ├── __init__.py
│   │
│   ├── services/                  # External AI Connectors & Scraping
│   │   ├── __init__.py
│   │   ├── github_scraper.py      # GitHub REST/GraphQL API Repo Analyzer
│   │   ├── stt_service.py         # Speech-To-Text client (Deepgram / Whisper)
│   │   ├── llm_service.py         # Gemini client + Context Caching logic
│   │   └── tts_service.py         # Text-To-Speech client (Cartesia / ElevenLabs)
│   │
│   ├── core/                      # Media & Pipeline Infrastructure
│   │   ├── __init__.py
│   │   ├── vad.py                 # Silero VAD wrapper & turn detection
│   │   ├── pipeline.py            # STT -> LLM -> TTS streaming event loop
│   │   └── context_builder.py    # Merges Resume JSON + Scraped GitHub text
│   │
│   ├── server/                    # API & Signaling Routes
│   │   ├── __init__.py
│   │   ├── signaling.py           # WebRTC SDP/ICE offer-answer routes
│   │   └── session_manager.py     # In-memory interview session state
│   │
│   ├── config.py                  # Module-specific settings & API keys
│   └── router.py                  # FastAPI APIRouter exposing interview endpoints
│
└── .env                           # Shared environment keys







How the Flow Works Step-by-Step
Initialization Route (POST /api/interview/init):

Accepts candidate's parsed_resume, target job title, and github_username.

github_scraper.py fetches their top repos, languages, and README files.

context_builder.py bundles Resume + GitHub into a single prompt payload.

llm_service.py registers this payload in Gemini Context Cache and returns a cache_id.

session_manager.py creates a unique session_id.

Signaling Route (POST /api/interview/signaling):

The browser initiates a WebRTC connection.

signaling.py handles the SDP exchange, creating a WebRTC peer connection strictly between Browser and Backend.

Live Interview Loop:

Microphone audio packets flow into vad.py.

Once vad.py detects a user turn complete, audio is sent to stt_service.py.

Transcribed text is sent to llm_service.py (referencing the cache_id).

Gemini response text is streamed to tts_service.py.

Generated raw audio bytes are sent straight back down the WebRTC stream to the browser speaker.