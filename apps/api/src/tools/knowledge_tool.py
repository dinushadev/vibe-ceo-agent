"""
Knowledge Tool (Agent-as-a-Tool)
Delegates research and learning requests to the KnowledgeAgent.
"""

import logging
from typing import Dict, Any, Optional

from src.db.database import get_database
from src.agents.knowledge_agent import KnowledgeAgent

logger = logging.getLogger(__name__)

# Global instance
_knowledge_agent = None

async def get_knowledge_agent():
    global _knowledge_agent
    if _knowledge_agent is None:
        db = await get_database()
        _knowledge_agent = KnowledgeAgent(db)
    return _knowledge_agent

async def consult_knowledge_wrapper(topic: str) -> str:
    """
    Use this tool to handle requests related to:
    - Researching or learning about a specific topic (e.g., "tell me about MCP", "how does photosynthesis work").
    - Explaining complex concepts.
    - Finding information from the web.
    
    Args:
        topic: The specific topic or question to research.
    """
    logger.info(f"Consulting Knowledge Agent with topic: {topic}")
    
    try:
        agent = await get_knowledge_agent()
        # Use a fixed user_id for now, consistent with other parts of the system
        user_id = "user_123"
        
        response = await agent.process_message(user_id, topic)
        
        # Extract the text response from the agent's result
        response_text = response.get("response", "I couldn't find information on that topic.")
        
        logger.info("Knowledge Agent consulted successfully")
        return response_text
        
    except Exception as e:
        logger.error(f"Error consulting Knowledge Agent: {e}", exc_info=True)
        return "I encountered an error while trying to consult the knowledge base."
