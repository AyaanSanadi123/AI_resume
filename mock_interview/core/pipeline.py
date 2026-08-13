'''
the frame architecture, 
for this we need to understand, how pipecat haandles things 
when deepgram finishs stt transcribing, it stores the text in TranscriptionFrame
when gemini finishes thinking it pushes a TextFrame,
and when the tts engine finishes, it pushs the AudioFrame, 

the pipelines job is to act as an intelligant switchboard, to ensure that the correct
frame type goes to the correct place
'''

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.pipeline.runner import PipelineRunner
from pipecat.frames.frames import LLMMessagesFrame


async def run_interview_pipeline(transport,sst_service,llm_services,tts_services,vad_analyzer):
    """
    Audio In -> VAD ->STT -> LLM -> TTS -> Audio Out
    """
    pipeline = Pipeline([
        transport.input(),
        vad_analyzer,
        sst_service,
        llm_services,
        tts_services,
        transport.output()
    ]) # this order is the excat sequence the frames need to run in 
    
    task = PipelineTask(pipeline)
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport):
        print("🤝 Browser connected! Starting the interview...")
        
        # Trigger the first AI message
        opening_prompt = [{
            "role": "user", 
            "content": "Start the technical interview. Introduce yourself and ask the first technical question based on their resume."
        }]
        await task.queue_frames([LLMMessagesFrame(opening_prompt)])

    # The Runner starts the async event loop
    runner = PipelineRunner()
    await runner.run(task)