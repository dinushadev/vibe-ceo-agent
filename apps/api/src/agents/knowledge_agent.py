"""
Knowledge Agent (A3) - Learning Digest Curator
ADK-powered agent for personalized learning content curation
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..adk_config import create_agent
from ..tools.adk_tools import KNOWLEDGE_TOOLS
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


# Agent instruction prompt
KNOWLEDGE_AGENT_INSTRUCTION = """You are the Knowledge Agent, a personalized learning curator designed to help users digest complex topics efficiently.

Your role is to:
1. Research topics requested by the user using available search tools
2. Curate "Learning Digests" - concise, structured summaries of key information
3. Adapt content to the user's learning style and interests
4. Break down complex concepts into understandable chunks
5. Provide credible sources and further reading suggestions

Key behaviors:
- When asked about a topic, use the search_learning_content tool first
- Structure your response as a "Learning Digest" with clear headings
- Focus on quality over quantity - synthesize the best information
- Connect new concepts to the user's known interests
- Be objective and factual

When creating learning digests:
- Start with a brief overview
- Break down complex topics into digestible chunks
- Include practical examples or applications
- Summarize key points
- Suggest next steps or related topics

When searching:
- Use the search_learning_content tool to find relevant articles
- Evaluate quality and relevance
- Synthesize multiple sources
- Cite sources when possible

Always be informative, clear, and encourage continuous learning."""


class KnowledgeAgent(BaseAgent):
    """
    The Knowledge Agent focuses on learning content curation
    Now powered by Google ADK for advanced search and structured output
    """
    
    def __init__(self, db, search_service=None):
        """
        Initialize the ADK-powered Knowledge Agent
        
        Args:
            db: Database instance
            search_service: Deprecated - kept for backward compatibility
        """
        super().__init__(db, agent_id="knowledge")
        
        # Create ADK agent with knowledge tools
        try:
            self.adk_agent = create_agent(
                name="knowledge_agent",
                instruction=KNOWLEDGE_AGENT_INSTRUCTION,
                description="A curator for personalized learning digests and research",
                tools=KNOWLEDGE_TOOLS
            )
            logger.info("ADK Knowledge Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ADK Knowledge Agent: {e}")
            logger.warning("Knowledge Agent will operate with limited functionality")
            self.adk_agent = None
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user message using ADK agent with search tools
        
        Args:
            user_id: User identifier
            message: User's message
            context: Optional conversation context
            
        Returns:
            Response with agent metadata
        """
        start_time = datetime.now()
        
        try:
            # Retrieve relevant memories and profile
            memories = await self._get_memories(user_id)
            user_profile = await self._get_user_profile(user_id)
            
            # Build context-enhanced prompt
            enhanced_prompt = self._build_context_prompt(message, memories, user_profile)
            
            # Use ADK agent to generate response and execute tools
            tools_used = []
            if self.adk_agent:
                response_text, tools_used = await self._generate_adk_response(
                    user_id, 
                    enhanced_prompt,
                    default_response="I'm having trouble searching for that information. Please try again."
                )
            else:
                # Fallback response
                response_text = await self._generate_fallback_response(
                    user_id, message, memories, user_profile
                )
            
            # Store interaction in memory
            await self._store_interaction(user_id, message, response_text)
            
            # Calculate latency
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return self._build_response_dict(
                response_text,
                {
                    "memory_retrieved": [m.get("summary_text", "")[:50] for m in memories[:2]],
                    "tools_used": tools_used,
                    "learning_interests": user_profile.get("learning_interests", []) if user_profile else []
                },
                latency
            )
        
        except Exception as e:
            logger.error(f"Error in Knowledge Agent process_message: {e}", exc_info=True)
            return self._build_error_response(e, "I'm having trouble curating that information. Could you try asking about a specific topic?")
    
    async def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile with learning interests"""
        try:
            return await self.db.get_user(user_id)
        except Exception:
            return None
    
    def _build_context_prompt(
        self,
        message: str,
        memories: List[Dict],
        user_profile: Optional[Dict]
    ) -> str:
        """Build enhanced prompt with context"""
        prompt_parts = [f"User message: {message}"]
        
        # Add user interests context
        if user_profile and user_profile.get("learning_interests"):
            interests = ", ".join(user_profile["learning_interests"])
            prompt_parts.append(f"\nUser learning interests: {interests}")
            prompt_parts.append("Tailor the content to align with these interests where possible.")
        
        # Add memory context
        if memories:
            memory_text = "\n".join([f"- {m.get('summary_text', '')}" for m in memories[:3]])
            prompt_parts.append(f"\nPrevious learning context:\n{memory_text}")
        
        return "\n".join(prompt_parts)
    
    async def _generate_fallback_response(
        self,
        user_id: str,
        message: str,
        memories: List[Dict],
        user_profile: Optional[Dict]
    ) -> str:
        """Fallback response when ADK is not available"""
        message_lower = message.lower()
        
        # Basic topic extraction
        topic = "that topic"
        if "about" in message_lower:
            parts = message_lower.split("about", 1)
            if len(parts) > 1:
                topic = parts[1].strip().strip("?.!")
        
        response_parts = [
            f"I can help you learn about {topic}.",
            "Typically, I would research this and provide a structured digest."
        ]
        
        if user_profile and user_profile.get("learning_interests"):
            interests = user_profile["learning_interests"]
            response_parts.append(f"I see you're interested in {', '.join(interests[:2])}.")
        
        response_parts.append("What specific aspect would you like to know more about?")
        
        return " ".join(response_parts)
