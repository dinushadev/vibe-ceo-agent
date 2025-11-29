"""
Personal Vibe CEO System - FastAPI Backend
Main entry point for the Python agent service
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import database and orchestrator
from src.db.database import get_database
from src.orchestrator import Orchestrator
from src.orchestrator import Orchestrator
from src.services.voice_service import VoiceService
from src.memory.memory_service import get_memory_service
import asyncio
import base64

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
db = None
orchestrator = None
voice_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI application"""
    global db, orchestrator, voice_service
    
    logger.info("Starting Personal Vibe CEO System API...")
    
    # Initialize database
    db = await get_database()
    logger.info("Database initialized")
    
    # Initialize orchestrator with all agents
    orchestrator = Orchestrator(db)
    logger.info("Orchestrator and agents initialized")

    # Initialize Memory Service (Singleton)
    get_memory_service(db)
    logger.info("Memory Service initialized")

    # Initialize Voice Service
    voice_service = VoiceService()
    logger.info("Voice Service initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Personal Vibe CEO System API...")
    if db:
        await db.close()


# Create FastAPI application
app = FastAPI(
    title="Personal Vibe CEO System",
    description="Multi-agent AI system with Google ADK",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Personal Vibe CEO System",
        "version": "1.0.0",
        "agents": ["vibe", "planner", "knowledge"],
        "adk_enabled": True
    }


@app.get("/api/status")
async def get_status():
    """Get system status including ADK agent information"""
    try:
        agent_status = orchestrator.get_agent_status()
        
        return {
            "status": "operational",
            "service": "Personal Vibe CEO System (ADK-Powered)",
            "version": "1.0.0",
            "timestamp": "2025-11-24T17:53:00Z",
            "adk_integration": agent_status
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }


@app.post("/api/chat")
async def chat(request: dict):
    """
    Main conversational endpoint for text-based chat
    
    Request body:
    {
        "user_id": "string",
        "message": "string",
        "context": {
            "agent_preference": "vibe" | "planner" | "knowledge",
            "session_id": "string"
        }
    }
    """
    try:
        user_id = request.get("user_id")
        message = request.get("message")
        context = request.get("context", {})
        
        if not user_id or not message:
            raise HTTPException(status_code=400, detail="Missing required fields: user_id and message")
        
        logger.info(f"Chat request from user {user_id}: {message[:50]}...")
        
        # Route to orchestrator
        response = await orchestrator.process_message(user_id, message, context)
        
        logger.info(f"Response from {response.get('agent_type')} agent")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/proactive-check")
async def proactive_check(user_id: str):
    """
    Check if proactive outreach is needed for a user (FR1)
    
    This endpoint can be called periodically to trigger proactive messages
    """
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id")
        
        logger.info(f"Checking proactive triggers for user {user_id}")
        
        # Check with orchestrator
        proactive_message = await orchestrator.check_proactive_triggers(user_id)
        
        if proactive_message:
            logger.info(f"Proactive message triggered for user {user_id}")
            return {
                "triggered": True,
                "message": proactive_message
            }
        else:
            return {
                "triggered": False,
                "message": None
            }
    
    except Exception as e:
        logger.error(f"Error in proactive check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config/user")
async def get_user_config(user_id: str):
    """Get user configuration and profile"""
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id")
        
        logger.info(f"Fetching config for user {user_id}")
        
        # Fetch from database
        user_data = await db.get_user(user_id)
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get health logs
        health_logs = await db.get_user_health_logs(user_id, limit=7)
        
        # Get memory summary
        vibe_memories = await db.get_agent_memories(user_id, "vibe", limit=10)
        planner_memories = await db.get_agent_memories(user_id, "planner", limit=10)
        knowledge_memories = await db.get_agent_memories(user_id, "knowledge", limit=10)
        
        total_memories = len(vibe_memories) + len(planner_memories) + len(knowledge_memories)
        
        return {
            "user": user_data,
            "health_logs": health_logs,
            "memory_summary": {
                "total_contexts": total_memories,
                "recent_interactions": len(health_logs)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user_config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config/user")
async def update_user_config(request: dict):
    """Update user configuration"""
    try:
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id")
        
        logger.info(f"Updating config for user {user_id}")
        
        # Update database
        name = request.get("name")
        learning_interests = request.get("learning_interests")
        
        updated_user = await db.update_user(
            user_id=user_id,
            name=name,
            learning_interests=learning_interests
        )
        
        return {
            "status": "success",
            "message": "User config updated",
            "user": updated_user
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_user_config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WebSocket Endpoint for Voice Streaming
# ============================================================================

@app.websocket("/api/live-stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for bidirectional voice streaming
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    # Queue for audio chunks
    audio_queue = asyncio.Queue()
    
    async def audio_generator():
        """Yields audio chunks from the queue"""
        while True:
            chunk = await audio_queue.get()
            if chunk is None: # Sentinel
                break
            yield chunk

    async def receive_audio():
        """Receive audio from WebSocket and put in queue"""
        try:
            while True:
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "audio_chunk":
                    # Expecting base64 encoded audio
                    payload = data.get("payload")
                    if payload:
                        try:
                            chunk = base64.b64decode(payload)
                            await audio_queue.put(chunk)
                        except Exception as e:
                            logger.error(f"Error decoding audio chunk: {e}")
                
                elif message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "payload": {},
                        "timestamp": "2025-11-24T13:51:00Z"
                    })
                    
        except WebSocketDisconnect:
            logger.info("WebSocket connection closed")
            await audio_queue.put(None) # Signal end of stream
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")
            await audio_queue.put(None)

    async def process_audio():
        """Process audio stream and send responses using Native Audio"""
        
        while True:
            try:


                # Create the generator INSIDE the loop to reuse for new sessions
                # This is critical because the previous session might have cancelled the generator
                audio_gen = audio_generator()

                logger.info("Starting VoiceService stream processing...")
                # Process the stream with Native Audio
                async for result in voice_service.process_audio_stream(audio_gen):
                    audio_bytes = result.get("audio")
                    
                    if audio_bytes:
                        # Send audio response directly
                        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                        await websocket.send_json({
                            "type": "audio_response",
                            "payload": audio_b64
                        })
                
                # If the generator finishes normally (e.g. session ended by model), we loop back to reconnect
                logger.info("Audio stream finished normally, reconnecting for next turn...")
                
                # Check if WebSocket is still open before reconnecting
                if websocket.client_state == WebSocketDisconnect:
                     logger.info("WebSocket client disconnected, stopping process_audio")
                     break
                        
            except Exception as e:
                logger.error(f"Error processing audio (will reconnect): {e}")
                # Check if WebSocket is still open
                if websocket.client_state == WebSocketDisconnect:
                    logger.info("WebSocket closed, stopping process_audio")
                    break
                
                # Brief pause before reconnecting to avoid tight loops
                await asyncio.sleep(0.5)

    # Run receive and process loops concurrently
    try:
        await websocket.send_json({
            "type": "connection_ack",
            "payload": {"status": "connected"},
            "timestamp": "2025-11-24T13:51:00Z"
        })
        
        await asyncio.gather(receive_audio(), process_audio())
        
    except Exception as e:
        logger.error(f"WebSocket handler error: {e}")
        try:
            await websocket.close(code=1011)
        except:
            pass


# ============================================================================
# Run the application
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
