# mock_interview/core/vad.py

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams

class InterviewVAD:
    
    def get_vad() -> SileroVADAnalyzer:
        print("🎛️ Initializing Silero VAD Analyzer...")
        return SileroVADAnalyzer(
            params=VADParams(
                stop_secs=0.6,   # Wait 600ms of silence before assuming user finished speaking
                start_secs=0.2,  # Trigger speech detection quickly
                confidence=0.7   # Strict confidence to ignore background noise
            )
        )