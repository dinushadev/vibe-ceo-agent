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
from src.memory.memory_service import get_memory_service

logger = logging.getLogger(__name__)

class KnowledgeTool:
    """
    Intelligent Knowledge Agent exposed as a tool.
    """
    
    def __init__(self):
        self.search_service = get_search_service()
        self.memory_service = get_memory_service()
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
        
        # Get Memory Context
        short_term_context = ""
        long_term_memories = []
        if self.memory_service:
            # Use a default user_id for MVP
            user_id = "user_123" 
            short_term_context = self.memory_service.get_short_term_context(user_id)
            long_term_memories = await self.memory_service.get_agent_memories(user_id, "knowledge", query=topic)
        
        # 2. Synthesize with Secondary LLM
        if not self.client:
            return "I'm having trouble accessing my knowledge base right now. Please try again later."
            
        # Format results for context
        results_str = json.dumps(search_results, indent=2)
        
        # Format memory string
        memory_str = ""
        if long_term_memories:
            memory_str = "\nRELEVANT PAST LEARNINGS:\n" + "\n".join([f"- {m.get('summary_text', '')}" for m in long_term_memories[:3]])
        
        if short_term_context:
            memory_str += f"\n\nCURRENT CONVERSATION:\n{short_term_context}"
        
        prompt = f"""
        You are the Knowledge Agent for the Personal Vibe CEO system.
        Your goal is to explain complex topics simply and concisely.
        
        TOPIC: "{topic}"
        
        MEMORY CONTEXT:
        {memory_str}
        
        SEARCH RESULTS:
        {results_str}
        
        INSTRUCTIONS:
        1. Synthesize the search results into a clear, easy-to-understand explanation.
        2. Use the MEMORY CONTEXT to connect to previous topics if relevant.
        3. Focus on the most relevant information for the user.
        4. If the topic is related to health/well-being, emphasize practical tips.
        5. Keep the response conversational and suitable for voice output (avoid complex lists or markdown).
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            summary = response.text
            logger.info("Knowledge generated summary successfully")
            
            # 3. Store Interaction in Memory
            if self.memory_service:
                user_id = "user_123"
                # Add to Short-Term
                self.memory_service.add_to_short_term(user_id, "user", topic)
                self.memory_service.add_to_short_term(user_id, "model", summary)
                # Add to Long-Term
                await self.memory_service.summarize_interaction(user_id, "knowledge", topic, summary)
            
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
