import os
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, List
from google import genai
from google.genai import types
from src.memory.memory_service import get_memory_service

from src.services.stt_service import AsyncSTTService

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

logger = logging.getLogger(__name__)

class VoiceService:
    """
    Service for handling Voice interactions using Gemini Native Audio (Multimodal Live API).
    Now acts as the Orchestrator using Agent-as-a-Tool pattern.
    """

    def __init__(self):
        """Initialize Google GenAI client"""
        try:
            self.client = genai.Client(
                http_options={'api_version': 'v1alpha'}
            )
            self.model_id = "gemini-2.5-flash-native-audio-preview-09-2025"
            self.memory_service = get_memory_service()
            self.stt_service = AsyncSTTService()
            
            # Define the Vibe CEO Persona
            self.system_instruction = """
            You are the "Personal Vibe CEO". 
            Your goal is to help the user achieve PEAK PERFORMANCE and WELL-BEING.
            
            CORE PERSONALITY:
            - Empathetic, supportive, and "vibey".
            - You care about the user's stress levels and health.
            - You are proactive but respectful.
            
            CAPABILITIES:
            1. GENERAL CHAT: If the user just wants to talk, vent, or reflect, respond directly with your Vibe persona.
            2. PLANNING: If the user needs to schedule, organize, or fix their day, use the 'consult_planner' tool.
            3. KNOWLEDGE: If the user wants to learn, research, or understand a topic, use the 'consult_knowledge' tool.
            
            AUDIO INSTRUCTIONS:
            - Speak naturally and conversationally.
            - Keep responses concise (users are listening, not reading).
            - Use a warm, encouraging tone.

            MEMORY CAPABILITIES:
            - You can REMEMBER facts, preferences, and medical info using tools.
            - If the user tells you something important (e.g., "I'm allergic to peanuts"), SAVE it.
            - Use `get_user_profile` to recall facts if needed.
            """
            
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
            
            logger.info(f"VoiceService initialized with model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize VoiceService: {e}")
            self.client = None

    async def process_audio_stream(self, audio_generator: AsyncGenerator[bytes, None]) -> AsyncGenerator[Dict, None]:
        """
        Process bidirectional audio stream with Gemini.
        """
        if not self.client:
            logger.error("GenAI client not initialized")
            return

        # Configure the session with tools and system instruction
        
        # 1. Fetch Memory Context
        user_id = "user_123" # Default for MVP
        memory_context = ""
        
        if self.memory_service:
            try:
                # Get Short-Term (Session) Context
                short_term = self.memory_service.get_short_term_context(user_id)
                
                # Get Long-Term (Vector) Context
                long_term = await self.memory_service.get_agent_memories(user_id, "vibe", limit=3)
                
                if short_term or long_term:
                    memory_context = "\n\nMEMORY CONTEXT:\n"
                    if long_term:
                        memory_context += "Relevant Past Details:\n" + "\n".join([f"- {m.get('summary_text', '')}" for m in long_term]) + "\n"
                    if short_term:
                        memory_context += f"\n{short_term}"
            except Exception as e:
                logger.error(f"Failed to fetch memory context for voice: {e}")

        # 2. Update System Instruction
        dynamic_system_instruction = self.system_instruction + memory_context

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
                                    if self.memory_service:
                                        self.memory_service.add_to_short_term(user_id, "model", text_content)

                        # Handle Audio Response
                        if response.data:
                            logger.info("VoiceService: Received audio chunk")
                            yield {
                                "audio": response.data,
                                "text": None
                            }
                        
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
