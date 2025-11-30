"""
ADK Utilities - Shared functions for ADK agent operations
Consolidates common patterns used across all agents
"""

import logging
from typing import AsyncIterator, Tuple, List, Dict, Optional
from datetime import datetime
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from src.adk_types import Content, Part

logger = logging.getLogger(__name__)


# Global session service instance (shared across all agents)
_session_service = None


def get_session_service() -> InMemorySessionService:
    """
    Get or create the global session service instance
    
    Returns:
        InMemorySessionService instance
    """
    global _session_service
    if _session_service is None:
        _session_service = InMemorySessionService()
        logger.info("Initialized global ADK session service")
    return _session_service


async def get_or_create_session(user_id: str, app_name: str = "vibe_ceo") -> str:
    """
    Get or create a session for a user
    
    Args:
        user_id: User identifier
        app_name: Application name
        
    Returns:
        Session ID
    """
    session_service = get_session_service()
    session_id = f"session_{user_id}"
    
    try:
        session = await session_service.get_session(
            session_id=session_id,
            user_id=user_id,
            app_name=app_name
        )
        
        if session:
            logger.debug(f"Retrieved existing session: {session_id}")
        else:
            await session_service.create_session(
                session_id=session_id,
                user_id=user_id,
                app_name=app_name
            )
            logger.info(f"Created new session: {session_id}")
            
    except Exception as e:
        logger.error(f"Error managing session {session_id}: {e}")
        # Try to create anyway as fallback if get failed weirdly
        try:
            await session_service.create_session(
                session_id=session_id,
                user_id=user_id,
                app_name=app_name
            )
        except Exception:
            pass # If create fails too, we'll likely fail later, but worth a try
    
    return session_id


def extract_text_from_adk_chunks(chunks: AsyncIterator) -> Tuple[str, List[str]]:
    """
    Extract text content and tool calls from ADK response chunks
    
    This function handles multiple response formats:
    - Direct string chunks
    - Objects with .text attribute
    - Content objects with nested Parts
    - Dictionary formats
    
    Args:
        chunks: Async iterator of ADK response chunks
        
    Returns:
        Tuple of (extracted_text, tool_names_used)
    """
    async def _extract():
        full_response_text = ""
        all_tool_calls = []
        
        async for chunk in chunks:
            # Extract text from ADK response chunks
            if isinstance(chunk, str):
                full_response_text += chunk
            elif hasattr(chunk, "text"):
                # Direct text attribute
                full_response_text += chunk.text
            elif hasattr(chunk, "content") and hasattr(chunk.content, "parts"):
                # Content object with parts
                for part in chunk.content.parts:
                    if hasattr(part, "text") and part.text:
                        full_response_text += part.text
                    if hasattr(part, "tool_code"):
                        all_tool_calls.append({"name": part.tool_code})
            elif isinstance(chunk, dict):
                # Dictionary format
                if "text" in chunk and chunk["text"]:
                    full_response_text += chunk["text"]
                elif "content" in chunk and "parts" in chunk["content"]:
                    for part in chunk["content"]["parts"]:
                        if "text" in part and part["text"]:
                            full_response_text += part["text"]
                        if "tool_code" in part:
                            all_tool_calls.append({"name": part["tool_code"]})
                if "tool_calls" in chunk:
                    all_tool_calls.extend(chunk["tool_calls"])
            # Skip other chunk types (metadata, usage stats, etc.)
        
        # Extract tool names
        tools_used = [call.get("name") for call in all_tool_calls if call.get("name")]
        
        return full_response_text.strip(), tools_used
    
    return _extract()


async def create_adk_runner(
    agent,
    user_id: str,
    prompt: str,
    app_name: str = "vibe_ceo"
) -> Tuple[str, List[str]]:
    """
    Create an ADK runner and execute the agent with the given prompt
    
    Args:
        agent: ADK LlmAgent instance
        user_id: User identifier
        prompt: User prompt/message
        app_name: Application name
        
    Returns:
        Tuple of (response_text, tools_used)
    """
    try:
        # Get or create session
        session_id = await get_or_create_session(user_id, app_name)
        
        # Initialize tracer
        tracer = get_agent_tracer()
        tracer.clear() # Reset for new run
        tracer.add_step("start", "Agent execution started", {"user_id": user_id, "prompt": prompt})
        
        # Create runner with session service
        runner = Runner(
            agent=agent,
            session_service=get_session_service(),
            app_name=app_name
        )
        
        # Run the agent and extract response
        chunks = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(role="user", parts=[Part(text=prompt)])
        )
        
        response_text, tools_used = await extract_text_from_adk_chunks(chunks)
        
        # Finalize trace
        tracer.add_step("complete", "Agent execution completed", {"response_length": len(response_text)})
        tracer.end_trace()
        
        return response_text, tools_used
        
    except Exception as e:
        logger.error(f"ADK runner execution failed: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"ADK runner execution failed: {e}", exc_info=True)
        raise


class AgentTracer:
    """
    Tracks full agent execution lifecycle including:
    - Overall latency
    - Tool executions (inputs, outputs, duration)
    - Agent steps/reasoning
    """
    
    def __init__(self):
        self._trace = {
            "start_time": datetime.utcnow().isoformat(),
            "steps": [],
            "tools": [],
            "metadata": {}
        }
        self._start_ts = datetime.now()
        
    def add_tool_execution(self, tool_name: str, input_data: dict, output_data: dict, duration_ms: int = 0):
        """Record a tool execution"""
        self._trace["tools"].append({
            "tool": tool_name,
            "input": input_data,
            "output": output_data,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    def add_step(self, step_type: str, content: str, metadata: Optional[Dict] = None):
        """Record an agent step (thought, response, etc)"""
        self._trace["steps"].append({
            "type": step_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        })
        
    def end_trace(self):
        """Finalize the trace"""
        self._trace["end_time"] = datetime.utcnow().isoformat()
        self._trace["total_duration_ms"] = int((datetime.now() - self._start_ts).total_seconds() * 1000)
        
    def get_trace(self) -> Dict:
        """Get the complete trace"""
        return self._trace
        
    def clear(self):
        self.__init__()

# Global tracer instance
# In production, use ContextVar for async safety
_agent_tracer = AgentTracer()

def get_agent_tracer():
    return _agent_tracer

# Backward compatibility
def get_tool_tracker():
    return _agent_tracer

# Update ToolExecutionTracker to alias AgentTracer for backward compat if needed
ToolExecutionTracker = AgentTracer
