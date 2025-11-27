import os
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, List
from google import genai
from google.genai import types

# Import Agent Tools
from src.tools.planner_tool import consult_planner_wrapper
from src.tools.knowledge_tool import consult_knowledge_wrapper

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
            """
            
            # Define Tools
            self.tools = [consult_planner_wrapper, consult_knowledge_wrapper]
            
            logger.info(f"VoiceService initialized with model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize VoiceService: {e}")
            self.client = None

    async def process_audio_stream(self, audio_generator: AsyncGenerator[bytes, None]) -> AsyncGenerator[Dict, None]:
        """
        Process bidirectional audio stream with Gemini.
        
        Args:
            audio_generator: Async generator yielding audio bytes chunks (input)
            
        Yields:
            Dict containing audio response payload
        """
        if not self.client:
            logger.error("GenAI client not initialized")
            return

        # Configure the session with tools and system instruction
        config = {
            "response_modalities": ["AUDIO"],
            "tools": self.tools,
            "system_instruction": self.system_instruction,
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

                # Task to send audio to the model
                async def send_audio():
                    try:
                        async for chunk in audio_generator:
                            if chunk:
                                await session.send(input={"data": chunk, "mime_type": "audio/pcm"}, end_of_turn=False)
                        logger.info("Audio generator finished, stopping send_audio")
                    except Exception as e:
                        logger.error(f"Error in send_audio task: {e}")
                        # We don't re-raise here to avoid crashing the gather, but the session might be dead

                # Start sending task
                send_task = asyncio.create_task(send_audio())

                try:
                    # Receive loop
                    async for response in session.receive():
                        # Log raw server content for debugging
                        if response.server_content:
                            logger.info("VoiceService: Received server_content event")

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
                                # Find and execute the matching tool
                                for tool in self.tools:
                                    if tool.__name__ == fc.name:
                                        try:
                                            # Execute the async tool wrapper
                                            tool_result = await tool(**fc.args)
                                            logger.info("VoiceService: Tool executed successfully")
                                        except Exception as e:
                                            logger.error(f"VoiceService: Tool execution failed: {e}")
                                            tool_result = f"Error executing tool {fc.name}: {str(e)}"
                                        break
                                
                                if tool_result:
                                    # Send tool response back to the model
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
                    # Wait for sender to finish
                    logger.info("Cancelling send_task")
                    send_task.cancel()
                    try:
                        await send_task
                    except asyncio.CancelledError:
                        pass

        except Exception as e:
            logger.error(f"Error in native audio stream: {e}")
            raise
