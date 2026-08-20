
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.pipeline.runner import PipelineRunner
from pipecat.frames.frames import LLMMessagesUpdateFrame


async def run_interview_pipeline(
    transport,
    stt_service,
    llm_service,
    tts_service,
    vad_analyzer
):
    """
    Audio In -> VAD -> STT -> LLM -> TTS -> Audio Out
    """

    pipeline = Pipeline([
        transport.input(),
        vad_analyzer,
        stt_service,
        llm_service,
        tts_service,
        transport.output()
    ])

    task = PipelineTask(pipeline)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport):
        print("🤝 Browser connected! Starting the interview...")

        # Trigger the first AI message
        opening_prompt = [{
            "role": "user",
            "content": (
                "Start the technical interview. "
                "Introduce yourself and ask the first technical "
                "question based on their resume."
            )
        }]

        await task.queue_frames([
            LLMMessagesUpdateFrame(messages=opening_prompt)
        ])

    # The Runner starts the async event loop
    runner = PipelineRunner()
    await runner.run(task)