"""
Orchestrator Core
Shared configuration and logic for Text and Voice Orchestrators.
"""

from .prompts import BASE_ORCHESTRATOR_INSTRUCTION, VIBE_AGENT_INSTRUCTION, VOICE_SYSTEM_INSTRUCTION
from ..tools.adk_tools import ORCHESTRATOR_TOOLS

def get_orchestrator_tools():
    """Get the unified list of tools for the Orchestrator"""
    return ORCHESTRATOR_TOOLS

def get_orchestrator_instruction(mode="text"):
    """
    Get the appropriate system instruction based on mode.
    
    Args:
        mode: "text" or "voice"
    """
    if mode == "voice":
        return VOICE_SYSTEM_INSTRUCTION
    return VIBE_AGENT_INSTRUCTION
