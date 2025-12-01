import os
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, List
from google import genai
from google.genai import types
from src.memory.memory_service import get_memory_service

from src.services.stt_service import AsyncSTTService

from src.agents.prompts import VOICE_SYSTEM_INSTRUCTION
from src.agents.context_utils import get_context_string
from src.db.database import get_database

# Import Agent Tools
from src.tools.planner_tool import consult_planner_wrapper
from src.tools.knowledge_tool import consult_knowledge_wrapper
from src.tools.memory_tools import (
    save_user_fact,
    get_user_profile,
    save_medical_info,
    get_medical_profile,
    save_user_preference
)
# Productivity tools removed to enforce delegation to PlannerAgent

logger = logging.getLogger(__name__)

class VoiceService:
    """
    Service for handling Voice interactions using Gemini Native Audio (Multimodal Live API).
    Now acts as the Orchestrator using Agent-as-a-Tool pattern.
    """

    def __init__(self):
        """Initialize VoiceService"""
        self.model_id = "gemini-2.5-flash-native-audio-preview-09-2025"
        self.memory_service = get_memory_service()
        self.stt_service = AsyncSTTService()
        self.stt_service = AsyncSTTService()
        self.client = None
        self.current_user_transcript = ""
        self.current_model_response = ""
        
        # Define the Vibe CEO Persona
        self.system_instruction = VOICE_SYSTEM_INSTRUCTION
        
        # Define Tools
        self.tools = [
            consult_planner_wrapper, 
            consult_knowledge_wrapper,
            save_user_fact,
            get_user_profile,
            save_medical_info,
            get_medical_profile,
            save_user_preference
        ]
        
        # Attempt initial initialization
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Google GenAI client"""
        try:
            self.client = genai.Client(
                http_options={'api_version': 'v1alpha'}
            )
            logger.info(f"VoiceService initialized with model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize VoiceService client: {e}")
            self.client = None

    async def process_audio_stream(self, audio_generator: AsyncGenerator[bytes, None]) -> AsyncGenerator[Dict, None]:
        """
        Process bidirectional audio stream with Gemini.
        """
        if not self.client:
            logger.warning("GenAI client not initialized, attempting to re-initialize...")
            self._initialize_client()
            
        if not self.client:
            raise RuntimeError("Failed to initialize GenAI client for audio streaming")

        # Configure the session with tools and system instruction
        
        # 1. Fetch Memory Context
        from src.context import get_current_user_id
        user_id = get_current_user_id()
        memory_context = ""
        personal_context = ""
        
        if self.memory_service:
            try:
                # Get Short-Term (Session) Context
                short_term = self.memory_service.get_short_term_context(user_id)
                
                # Get Long-Term (Vector) Context
                long_term = await self.memory_service.get_agent_memories(user_id, "vibe", limit=3)
                
                # Get Personal Context (Facts, Prefs, Medical, Tasks, Events)
                personal_context = await self.memory_service.get_user_context(user_id)
                logger.info(f"Voice Service: Retrieved personal context (length: {len(personal_context)})")
                
                if short_term or long_term or personal_context:
                    memory_context = "\n\nCONTEXT:\n"
                    
                    if personal_context:
                        memory_context += f"{personal_context}\n"
                    
                    if long_term:
                        memory_context += "Relevant Past Details:\n" + "\n".join([f"- {m.get('summary_text', '')}" for m in long_term]) + "\n"
                    
                    if short_term:
                        memory_context += f"\n{short_term}"
                    
                    logger.info(f"Voice Service: Full memory context length: {len(memory_context)}")
            except Exception as e:
                logger.error(f"Failed to fetch memory context for voice: {e}", exc_info=True)

        # 2. Update System Instruction
        # Use shared context utility to build the context string
        db = await get_database()
        context_string = await get_context_string(
            user_id=user_id,
            db=db,
            memories=long_term,
            personal_context=personal_context,
            short_term_context=short_term,
            include_time=True
        )
        
        dynamic_system_instruction = self.system_instruction + "\n\n" + context_string
        
        # Log the instruction to verify
        logger.info(f"Voice Service: System instruction updated. Length: {len(dynamic_system_instruction)}")
        logger.info(f"Voice Service: Instruction Tail (Context): {dynamic_system_instruction[-500:]}")

        config = {
            "response_modalities": ["AUDIO"],
            "tools": self.tools,
            "system_instruction": dynamic_system_instruction,
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": "Puck"
                    }
                }
            }
        }

        try:
            async with self.client.aio.live.connect(model=self.model_id, config=config) as session:
                logger.info("Connected to Gemini Live session with Tools")

                # STT Queue
                stt_queue = asyncio.Queue()

                # Generator for STT
                async def stt_generator():
                    while True:
                        chunk = await stt_queue.get()
                        if chunk is None:
                            break
                        yield chunk

                # Task to run STT
                async def run_stt():
                    if self.stt_service:
                        async for transcript in self.stt_service.transcribe(stt_generator()):
                            if transcript:
                                logger.info(f"User said: {transcript}")
                                # Store User Input in Memory
                                self.current_user_transcript = transcript
                                if self.memory_service:
                                    self.memory_service.add_to_short_term(user_id, "user", transcript)

                stt_task = asyncio.create_task(run_stt())

                # Task to send audio to the model AND STT
                async def send_audio():
                    try:
                        async for chunk in audio_generator:
                            if chunk:
                                # Send to Gemini
                                await session.send(input={"data": chunk, "mime_type": "audio/pcm"}, end_of_turn=False)
                                # Send to STT
                                stt_queue.put_nowait(chunk)
                                
                        logger.info("Audio generator finished, stopping send_audio")
                        stt_queue.put_nowait(None) # Signal STT to stop
                    except Exception as e:
                        logger.error(f"Error in send_audio task: {e}")

                # Start sending task
                send_task = asyncio.create_task(send_audio())

                try:
                    # Receive loop
                    async for response in session.receive():
                        # Handle Text Response (for Memory) - IF enabled in future
                        if response.server_content and response.server_content.model_turn:
                            for part in response.server_content.model_turn.parts:
                                if part.text:
                                    text_content = part.text
                                    self.current_model_response += text_content
                                    if self.memory_service:
                                        self.memory_service.add_to_short_term(user_id, "model", text_content)

                        # Handle Audio Response
                        if response.data:
                            logger.info("VoiceService: Received audio chunk")
                            yield {
                                "audio": response.data,
                                "text": None
                            }
                        
                        # Detect Turn End (simplistic: if we have both transcript and response)
                        # In a real system, we might wait for a specific "turn_complete" signal or silence
                        if response.server_content and response.server_content.turn_complete:
                             logger.info("VoiceService: Turn complete, storing interaction")
                             if self.current_user_transcript and self.current_model_response:
                                 await self._store_interaction(
                                     user_id, 
                                     self.current_user_transcript, 
                                     self.current_model_response
                                 )
                                 # Reset for next turn
                                 self.current_user_transcript = ""
                                 self.current_model_response = ""
                        
                        # Handle Tool Calls
                        if response.tool_call:
                            for fc in response.tool_call.function_calls:
                                logger.info(f"VoiceService: Executing tool: {fc.name}")
                                tool_result = None
                                for tool in self.tools:
                                    if tool.__name__ == fc.name:
                                        try:
                                            tool_result = await tool(**fc.args)
                                            logger.info("VoiceService: Tool executed successfully")
                                        except Exception as e:
                                            logger.error(f"VoiceService: Tool execution failed: {e}")
                                            tool_result = f"Error executing tool {fc.name}: {str(e)}"
                                        break
                                
                                if tool_result:
                                    tool_response = types.LiveClientToolResponse(
                                        function_responses=[
                                            types.FunctionResponse(
                                                name=fc.name,
                                                id=fc.id,
                                                response={"result": tool_result}
                                            )
                                        ]
                                    )
                                    logger.info("VoiceService: Sending tool response to model")
                                    await session.send(input=tool_response)
                
                except Exception as e:
                    logger.error(f"Error in receive loop: {e}")
                    raise
                finally:
                    # Cleanup
                    logger.info("Cancelling tasks")
                    send_task.cancel()
                    stt_task.cancel()
                    try:
                        await send_task
                        await stt_task
                    except asyncio.CancelledError:
                        pass

        except Exception as e:
            logger.error(f"Error in native audio stream: {e}")
            raise

    async def _store_interaction(
        self,
        user_id: str,
        user_message: str,
        agent_response: str
    ):
        """
        Store interaction in memory service (Short-Term & Long-Term)
        """
        if self.memory_service:
            try:
                # Note: Short-term is already added incrementally in the loop
                
                # Add to Long-Term Memory (Summarized)
                await self.memory_service.summarize_interaction(
                    user_id=user_id,
                    agent_id="vibe", # Voice acts as Vibe agent
                    user_message=user_message,
                    agent_response=agent_response
                )
                logger.info("VoiceService: Interaction stored in long-term memory")
            except Exception as e:
                logger.error(f"Failed to store interaction in memory: {e}")
