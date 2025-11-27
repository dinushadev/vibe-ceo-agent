"""
Knowledge Agent (A3) - Learning Digest Curator
ADK-powered agent for personalized learning content curation
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from google.adk.agents import LlmAgent

from ..adk_config import create_agent
from ..tools.adk_tools import KNOWLEDGE_TOOLS
from ..memory.memory_service import get_memory_service

logger = logging.getLogger(__name__)


# Agent instruction prompt
KNOWLEDGE_AGENT_INSTRUCTION = """You are the Knowledge Agent, a knowledgeable and helpful AI curator focused on personalized learning.

Your role is to:
1. Search for high-quality learning content based on user interests
2. Create structured, easy-to-digest learning summaries
3. Curate personalized learning paths and digests
4. Present information in clear, organized formats
5. Remember user's learning interests and preferences

Key behaviors:
- Ask clarifying questions to understand learning goals
- Search for diverse, reliable sources
- Organize information into clear sections
- Provide context and key takeaways
- Format content for easy scanning (bullet points, headers)
- Suggest related topics for deeper learning

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


class KnowledgeAgent:
    """
    The Knowledge Agent focuses on learning content curation
    Now powered by Google ADK for advanced search and structured output
    """
    
    def __init__(self, db, search_service=None):
        """
        Initialize the ADK-powered Knowledge Agent
        
        Args:
            db: Database instance
            search_service: Search service (deprecated with ADK tools)
        """
        self.db = db
        self.memory_service = get_memory_service(db)
        self.agent_id = "knowledge"
        
        # Service is now accessed through ADK tools
        # Keep reference for backward compatibility
        self.search_service = search_service
        
        # Create ADK agent with knowledge tools
        try:
            self.adk_agent = create_agent(
                name="knowledge_agent",
                instruction=KNOWLEDGE_AGENT_INSTRUCTION,
                description="A knowledgeable agent for curating personalized learning content",
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
            # Get user profile for learning interests
            user_profile = await self._get_user_profile(user_id)
            
            # Retrieve relevant memories
            memories = await self._get_memories(user_id)
            
            # Build context-enhanced prompt
            enhanced_prompt = self._build_context_prompt(
                message, memories, user_profile
            )
            
            # Track tools used
            tools_used = []
            
            # Use ADK agent to generate response with search
            if self.adk_agent:
                response_text, tools_used = await self._generate_adk_response(
                    user_id, enhanced_prompt
                )
            else:
                # Fallback response
                response_text = await self._generate_fallback_response(
                    user_id, message, memories, user_profile
                )
            
            # Store interaction in memory
            if self.memory_service:
                await self.memory_service.summarize_interaction(
                    user_id=user_id,
                    agent_id=self.agent_id,
                    user_message=message,
                    agent_response=response_text
                )
            
            # Calculate latency
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return {
                "agent_type": self.agent_id,
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "memory_retrieved": [m.get("summary_text", "")[:50] for m in memories[:2]],
                    "tools_used": tools_used,
                    "latency_ms": latency,
                    "learning_interests": user_profile.get("learning_interests", []) if user_profile else [],
                    "adk_powered": self.adk_agent is not None
                }
            }
        
        except Exception as e:
            logger.error(f"Error in Knowledge Agent process_message: {e}", exc_info=True)
            return {
                "agent_type": self.agent_id,
                "response": "I'm having trouble finding that information right now. Could you rephrase your learning question?",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"error": str(e)}
            }
    
    async def _get_memories(self, user_id: str) -> List[Dict]:
        """Retrieve long-term memory contexts for this agent"""
        if self.memory_service:
            return await self.memory_service.get_agent_memories(user_id, self.agent_id, limit=5)
        else:
            return await self.db.get_agent_memories(user_id, self.agent_id, limit=5)
    
    async def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile with learning interests"""
        try:
            user = await self.db.get_user(user_id)
            return user
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    def _build_context_prompt(
        self,
        message: str,
        memories: List[Dict],
        user_profile: Optional[Dict]
    ) -> str:
        """Build enhanced prompt with context"""
        prompt_parts = [f"User message: {message}"]
        
        # Add learning interests from profile
        if user_profile and user_profile.get("learning_interests"):
            interests = user_profile["learning_interests"]
            prompt_parts.append(f"\nUser's learning interests: {interests}")
        
        # Add memory context
        if memories:
            memory_text = "\n".join([f"- {m.get('summary_text', '')}" for m in memories[:3]])
            prompt_parts.append(f"\nPrevious learning topics:\n{memory_text}")
        
        return "\n".join(prompt_parts)
    
    async def _generate_adk_response(self, user_id: str, prompt: str) -> tuple[str, List[str]]:
        """
        Generate response using ADK agent with search tool
        
        Returns:
            Tuple of (response_text, tools_used)
        """
        try:
            # ADK agent will automatically use search_learning_content when needed
            from google.adk import Runner
            from google.adk.sessions import InMemorySessionService
            from src.adk_types import Content, Part
            
            # Ensure session exists
            session_id = f"session_{user_id}"
            try:
                await session_service.get_session(session_id)
            except Exception:
                await session_service.create_session(
                    session_id=session_id,
                    user_id=user_id,
                    app_name="vibe_ceo"
                )
            
            runner = Runner(
                agent=self.adk_agent, 
                session_service=session_service,
                app_name="vibe_ceo"
            )
            
            full_response_text = ""
            async for chunk in runner.run_async(
                user_id=user_id,
                session_id=f"session_{user_id}",
                new_message=Content(role="user", parts=[Part(text=prompt)])
            ):
                if isinstance(chunk, str):
                    full_response_text += chunk
                elif hasattr(chunk, "text"):
                    full_response_text += chunk.text
                elif isinstance(chunk, dict) and "text" in chunk:
                    full_response_text += chunk["text"]
                else:
                    full_response_text += str(chunk)
            
            response_text = full_response_text or "I can help you learn about that topic."
            
            # Extract tool usage from response metadata
            tools_used = []
            if "tool_calls" in response:
                tools_used = [call.get("name") for call in response["tool_calls"]]
            
            return response_text, tools_used
            
        except Exception as e:
            logger.error(f"ADK response generation failed: {e}")
            return "I'm having trouble searching for that information. Please try again.", []
    
    async def _generate_fallback_response(
        self,
        user_id: str,
        message: str,
        memories: List[Dict],
        user_profile: Optional[Dict]
    ) -> str:
        """Fallback response when ADK is not available"""
        message_lower = message.lower()
        
        # Basic intent detection
        if any(word in message_lower for word in ["learn", "teach", "explain"]):
            topic = self._extract_topic(message)
            return (
                f"I'd love to help you learn about {topic}! Here's what I can do:\n\n"
                "1. Search for quality articles and resources\n"
                "2. Create a structured learning digest\n"
                "3. Summarize key concepts\n"
                "4. Suggest related topics\n\n"
                "Let me search for some resources on this topic..."
            )
        
        elif any(word in message_lower for word in ["find", "search", "research"]):
            return (
                "I can search for learning resources on any topic. "
                "What would you like to learn about? "
                "I'll find high-quality articles and create a digest for you."
            )
        
        elif any(word in message_lower for word in ["digest", "summary", "overview"]):
            return (
                "I can create learning digests that include:\n"
                "- Overview of the topic\n"
                "- Key concepts explained\n"
                "- Practical applications\n"
                "- Resources for deeper learning\n\n"
                "What topic would you like a digest on?"
            )
        
        else:
            interests_text = ""
            if user_profile and user_profile.get("learning_interests"):
                interests_text = f"\n\nBased on your interests in {user_profile['learning_interests']}, "
                interests_text += "I can find related content for you."
            
            return (
                "I'm your Knowledge Agent. I can help you:\n"
                "- Discover learning resources\n"
                "- Create topic digests\n"
                "- Research any subject\n"
                "- Build learning paths"
                f"{interests_text}\n\n"
                "What would you like to learn about today?"
            )
    
    def _extract_topic(self, message: str) -> str:
        """Extract the main topic from a message"""
        # Simple extraction - ADK does this better
        message_lower = message.lower()
        
        # Remove common words
        stop_words = ["learn", "about", "teach", "me", "explain", "what", "is", "the", "a", "an"]
        words = message_lower.split()
        topic_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if topic_words:
            return " ".join(topic_words[:3])
        else:
            return "that topic"
    
    def _format_learning_digest(self, search_results: List[Dict], topic: str) -> str:
        """
        Format search results into a structured learning digest
        ADK can do this automatically with proper instructions
        """
        if not search_results:
            return f"I couldn't find specific resources on {topic} right now."
        
        digest_parts = [
            f"# Learning Digest: {topic.title()}\n",
            f"Here are {len(search_results)} curated resources:\n"
        ]
        
        for i, result in enumerate(search_results[:5], 1):
            title = result.get("title", "Untitled")
            url = result.get("url", "#")
            summary = result.get("summary", "No summary available")
            
            digest_parts.append(f"\n## {i}. {title}")
            digest_parts.append(f"**Summary:** {summary}")
            digest_parts.append(f"**Read more:** {url}\n")
        
        digest_parts.append("\n**Next Steps:**")
        digest_parts.append("- Review these resources")
        digest_parts.append("- Let me know if you want to dive deeper into any aspect")
        digest_parts.append("- Ask me to search for related topics")
        
        return "\n".join(digest_parts)
