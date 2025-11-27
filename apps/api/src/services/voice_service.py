import os
import logging
from typing import AsyncGenerator, Generator, Optional, Dict
from google.cloud import speech
from google.cloud import texttospeech

logger = logging.getLogger(__name__)

class VoiceService:
    """
    Service for handling Voice interactions using Google Cloud STT and TTS.
    """

    def __init__(self):
        """Initialize Google Cloud Speech and TTS clients"""
        try:
            # We use the async client for streaming recognition
            from google.cloud import speech_v1
            self.speech_client = speech_v1.SpeechAsyncClient()
            self.tts_client = texttospeech.TextToSpeechClient()
            logger.info("VoiceService initialized with Google Cloud clients")
        except Exception as e:
            logger.error(f"Failed to initialize VoiceService: {e}")
            self.speech_client = None
            self.tts_client = None

    def create_streaming_config(self) -> speech.StreamingRecognitionConfig:
        """Create the streaming configuration for STT"""
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )
        
        return streaming_config

    async def transcribe_stream(self, audio_generator: AsyncGenerator[bytes, None]) -> AsyncGenerator[Dict, None]:
        """
        Transcribe audio stream using Google Cloud STT.
        
        Args:
            audio_generator: Async generator yielding audio bytes chunks
            
        Yields:
            Dict containing transcript and is_final flag
        """
        if not self.speech_client:
            logger.error("Speech client not initialized")
            return

        streaming_config = self.create_streaming_config()
        logger.info("Starting transcription stream")

        try:
            # Generator that yields StreamingRecognizeRequest
            async def request_generator():
                # Initial config request
                yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)
                
                # Audio chunks
                async for chunk in audio_generator:
                    if chunk:
                        yield speech.StreamingRecognizeRequest(audio_content=chunk)

            # Perform streaming recognition
            responses = await self.speech_client.streaming_recognize(
                requests=request_generator()
            )

            async for response in responses:
                if not response.results:
                    continue
                    
                result = response.results[0]
                if not result.alternatives:
                    continue
                    
                transcript = result.alternatives[0].transcript
                
                # Yield both interim and final results
                yield {
                    "text": transcript,
                    "is_final": result.is_final
                }
                
                if result.is_final:
                    logger.info(f"Final transcript: {transcript}")

        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            # Don't re-raise, just stop the stream
            return

    async def synthesize_speech(self, text: str) -> Optional[bytes]:
        """
        Synthesize text to speech using Google Cloud TTS.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes (MP3)
        """
        if not self.tts_client:
            logger.error("TTS client not initialized")
            return None

        try:
            logger.info(f"Synthesizing speech for: {text[:50]}...")
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Use a more human-like 'Neural2' voice
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-D"  # Warm, expressive male voice
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # Run synchronous TTS in a thread pool to avoid blocking the event loop
            import asyncio
            from functools import partial
            
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    self.tts_client.synthesize_speech,
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
            )
            
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}", exc_info=True)
            return None
