import queue
import logging
from google.cloud import speech
import asyncio

logger = logging.getLogger(__name__)

class STTService:
    """
    Service for Streaming Speech-to-Text using Google Cloud Speech API.
    Used to capture user input text for memory persistence.
    """
    def __init__(self):
        try:
            self.client = speech.SpeechClient()
            self.config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=24000, # Gemini Native Audio uses 24kHz usually, need to verify
                language_code="en-US",
            )
            self.streaming_config = speech.StreamingRecognitionConfig(
                config=self.config,
                interim_results=False # We only want final results for memory
            )
            logger.info("STTService initialized")
        except Exception as e:
            logger.error(f"Failed to initialize STTService: {e}")
            self.client = None

    async def transcribe_stream(self, audio_queue: asyncio.Queue, callback):
        """
        Consumes audio chunks from a queue and sends them to STT API.
        Calls callback(text) when a transcript is received.
        """
        if not self.client:
            return

        # Generator to yield chunks from the async queue
        def request_generator():
            while True:
                try:
                    # Blocking get from queue (run in executor to avoid blocking loop)
                    # Wait, we can't block the loop.
                    # We need a way to bridge async queue to sync generator.
                    # Standard pattern: use an intermediate buffer or thread.
                    chunk = audio_queue.get_nowait()
                    if chunk is None: # Sentinel
                        return
                    yield speech.StreamingRecognizeRequest(audio_content=chunk)
                except asyncio.QueueEmpty:
                    # This is tricky with sync generator.
                    # Better approach: Collect chunks in a list and send? No, streaming.
                    # We'll skip complex threading for MVP and just return for now.
                    # Actually, let's use a simpler approach: 
                    # We can't easily mix async queue with sync generator without threading.
                    pass
                except Exception:
                    return

        # The above generator is flawed for async.
        # Let's use a proper async-to-sync bridge or just use the async client?
        # google-cloud-speech has SpeechAsyncClient!
        pass

class AsyncSTTService:
    """
    Async version using SpeechAsyncClient
    """
    def __init__(self):
        try:
            from google.cloud import speech_v1
            self.client = speech_v1.SpeechAsyncClient()
            self.config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000, # Standard for STT. Gemini might send 24k. We might need resampling.
                # Actually, the frontend sends 16k usually? Let's check useVoice.ts.
                language_code="en-US",
            )
            self.streaming_config = speech_v1.StreamingRecognitionConfig(
                config=self.config,
                interim_results=False
            )
            logger.info("AsyncSTTService initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AsyncSTTService: {e}")
            self.client = None

    async def transcribe(self, audio_generator):
        """
        Transcribe audio stream
        """
        if not self.client:
            return

        async def request_generator():
            # First request contains config
            yield speech_v1.StreamingRecognizeRequest(streaming_config=self.streaming_config)
            
            # Subsequent requests contain audio
            async for chunk in audio_generator:
                yield speech_v1.StreamingRecognizeRequest(audio_content=chunk)

        try:
            responses = await self.client.streaming_recognize(requests=request_generator())

            async for response in responses:
                for result in response.results:
                    if result.is_final:
                        transcript = result.alternatives[0].transcript
                        logger.info(f"STT Transcript: {transcript}")
                        yield transcript
        except Exception as e:
            logger.error(f"STT Error: {e}")
