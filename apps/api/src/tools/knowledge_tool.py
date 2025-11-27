"""
Knowledge Tool (Agent-as-a-Tool)
Uses a secondary LLM to synthesize search results into a concise briefing.
"""

import logging
import json
from typing import Dict, Any, Optional

from google import genai
from google.genai import types

from src.tools.mock_tools import get_search_service

logger = logging.getLogger(__name__)

class KnowledgeTool:
    """
    Intelligent Knowledge Agent exposed as a tool.
    """
    
    def __init__(self):
        self.search_service = get_search_service()
        self.model_id = "gemini-2.0-flash-exp"
        
        try:
            self.client = genai.Client(
                http_options={'api_version': 'v1alpha'}
            )
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client for Knowledge: {e}")
            self.client = None

    async def consult_knowledge(self, topic: str) -> str:
        """
        Researches a topic and provides a synthesized summary.
        
        Args:
            topic: The topic to research (e.g., "benefits of meditation", "quantum physics")
            
        Returns:
            A text response containing the synthesized information.
        """
        logger.info(f"Knowledge Tool invoked for topic: {topic}")
        
        # 1. Perform Search
        search_results = await self.search_service.search(topic, max_results=3)
        
        # 2. Synthesize with Secondary LLM
        if not self.client:
            return "I'm having trouble accessing my knowledge base right now. Please try again later."
            
        # Format results for context
        results_str = json.dumps(search_results, indent=2)
        
        prompt = f"""
        You are the Knowledge Agent for the Personal Vibe CEO system.
        Your goal is to explain complex topics simply and concisely.
        
        TOPIC: "{topic}"
        
        SEARCH RESULTS:
        {results_str}
        
        INSTRUCTIONS:
        1. Synthesize the search results into a clear, easy-to-understand explanation.
        2. Focus on the most relevant information for the user.
        3. If the topic is related to health/well-being, emphasize practical tips.
        4. Keep the response conversational and suitable for voice output (avoid complex lists or markdown).
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            summary = response.text
            logger.info("Knowledge generated summary successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Error in Knowledge LLM generation: {e}")
            return f"I found some information about {topic}, but I couldn't synthesize it properly."

# Global instance
_knowledge_tool = None

def get_knowledge_tool():
    global _knowledge_tool
    if _knowledge_tool is None:
        _knowledge_tool = KnowledgeTool()
    return _knowledge_tool

async def consult_knowledge_wrapper(topic: str) -> str:
    """
    Use this tool to handle requests related to:
    - Researching or learning about a specific topic (e.g., "tell me about MCP", "how does photosynthesis work").
    - Explaining complex concepts.
    - Finding information from the web.
    
    Args:
        topic: The specific topic or question to research.
    """
    tool = get_knowledge_tool()
    return await tool.consult_knowledge(topic)
