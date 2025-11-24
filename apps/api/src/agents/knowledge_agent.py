"""
Knowledge Agent (A3) - Personalized Learning Digest
Curates learning content based on user interests
"""

import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class KnowledgeAgent:
    """
    The Knowledge Agent curates personalized learning content
    
    Features:
    - Searches for relevant learning materials
    - Creates structured learning digests (O3)
    - Personalizes based on user interests
    - Logs search tool usage (NFR3)
    """
    
    def __init__(self, db, search_service):
        """
        Initialize the Knowledge Agent
        
        Args:
            db: Database instance for user data and logging
            search_service: Search tool service
        """
        self.db = db
        self.search_service = search_service
        self.agent_id = "knowledge"
        logger.info("KnowledgeAgent initialized")
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user message and generate learning content
        
        Args:
            user_id: User identifier
            message: User's message
            context: Optional conversation context
            
        Returns:
            Response with curated content
        """
        start_time = datetime.now()
        
        # Get user's learning interests
        user = await self.db.get_user(user_id)
        interests = user.get("learning_interests", []) if user else []
        
        # Determine if this is a digest request or a specific query
        intent = self._classify_knowledge_intent(message)
        
        if intent == "create_digest":
            result = await self._create_learning_digest(user_id, interests)
        elif intent == "search_topic":
            topic = self._extract_topic(message)
            result = await self._search_and_summarize(user_id, topic)
        else:
            result = {
                "response": "I can help you learn about topics you're interested in. Would you like me to create a personalized learning digest, or search for something specific?",
                "digest": None
            }
        
        # Calculate latency
        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            "agent_type": self.agent_id,
            "response": result["response"],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "tools_used": result.get("tools_used", []),
                "digest": result.get("digest"),
                "latency_ms": latency
            }
        }
    
    async def _create_learning_digest(
        self,
        user_id: str,
        interests: List[str]
    ) -> Dict:
        """
        Create a personalized learning digest (FR4, O3)
        
        This demonstrates:
        - Tool calling (search API)
        - Structured output generation
        """
        if not interests:
            return {
                "response": "I don't have your learning interests set up yet. What topics would you like to learn about?",
                "digest": None,
                "tools_used": []
            }
        
        # Pick the first interest for the digest
        topic = interests[0]
        
        tool_start = datetime.now()
        
        try:
            # Call search tool
            search_results = await self.search_service.search(topic, max_results=5)
            
            tool_time = int((datetime.now() - tool_start).total_seconds() * 1000)
            
            # Log tool action (NFR3)
            await self.db.log_tool_action(
                log_id=str(uuid.uuid4()),
                user_id=user_id,
                tool_name="search_service.search",
                input_query=f"Learning digest for: {topic}",
                output_result=f"Found {len(search_results)} articles",
                success=True,
                execution_time_ms=tool_time
            )
            
            # Generate structured learning digest (O3)
            digest = await self._format_digest(topic, search_results, interests)
            
            response = self._generate_digest_response(topic, len(search_results))
            
            return {
                "response": response,
                "digest": digest,
                "tools_used": ["search_service"]
            }
        
        except Exception as e:
            logger.error(f"Error creating learning digest: {e}")
            
            await self.db.log_tool_action(
                log_id=str(uuid.uuid4()),
                user_id=user_id,
                tool_name="search_service.search",
                input_query=f"Learning digest for: {topic}",
                output_result=f"Error: {str(e)}",
                success=False,
                execution_time_ms=int((datetime.now() - tool_start).total_seconds() * 1000)
            )
            
            return {
                "response": "I encountered an issue creating your learning digest. Please try again.",
                "digest": None,
                "tools_used": []
            }
    
    async def _search_and_summarize(self, user_id: str, topic: str) -> Dict:
        """Search for a specific topic and summarize results"""
        tool_start = datetime.now()
        
        try:
            search_results = await self.search_service.search(topic, max_results=5)
            
            tool_time = int((datetime.now() - tool_start).total_seconds() * 1000)
            
            await self.db.log_tool_action(
                log_id=str(uuid.uuid4()),
                user_id=user_id,
                tool_name="search_service.search",
                input_query=topic,
                output_result=f"Found {len(search_results)} results",
                success=True,
                execution_time_ms=tool_time
            )
            
            # Format results into a structured summary
            summary = self._format_search_summary(topic, search_results)
            
            response = f"I found {len(search_results)} articles about {topic}. Here's what I discovered:\n\n{summary}"
            
            return {
                "response": response,
                "digest": {
                    "topic": topic,
                    "sources": search_results,
                    "summary": summary
                },
                "tools_used": ["search_service"]
            }
        
        except Exception as e:
            logger.error(f"Error searching topic: {e}")
            return {
                "response": f"I had trouble searching for information about {topic}. Please try again.",
                "digest": None,
                "tools_used": []
            }
    
    async def _format_digest(
        self,
        topic: str,
        search_results: List[Dict],
        all_interests: List[str]
    ) -> Dict:
        """
        Format search results into a structured learning digest (O3)
        
        This creates the structured output required by FR4
        """
        # Extract key points from top results
        key_points = []
        for i, result in enumerate(search_results[:3], 1):
            key_points.append(f"{i}. {result['snippet']}")
        
        # Build comprehensive digest structure
        digest = {
            "topic": topic,
            "summary": f"A curated collection of resources about {topic} tailored to your learning interests.",
            "key_points": key_points,
            "sources": [
                {
                    "title": result["title"],
                    "url": result["url"],
                    "snippet": result["snippet"],
                    "relevance_score": result.get("relevance_score", 0.9)
                }
                for result in search_results
            ],
            "generated_at": datetime.now().isoformat(),
            "related_interests": [i for i in all_interests if i != topic]
        }
        
        return digest
    
    def _format_search_summary(self, topic: str, results: List[Dict]) -> str:
        """Format search results into a readable summary"""
        if not results:
            return "No results found."
        
        summary_parts = []
        
        for i, result in enumerate(results[:3], 1):
            summary_parts.append(
                f"{i}. **{result['title']}**\n"
                f"   {result['snippet']}\n"
                f"   Source: {result['url']}"
            )
        
        if len(results) > 3:
            summary_parts.append(f"\n...and {len(results) - 3} more resources")
        
        return "\n\n".join(summary_parts)
    
    def _generate_digest_response(self, topic: str, result_count: int) -> str:
        """Generate natural language response for digest creation"""
        return (
            f"📚 I've created a personalized learning digest about **{topic}** for you!\n\n"
            f"I found {result_count} curated articles and resources. "
            f"This digest includes:\n"
            f"- Key concepts and takeaways\n"
            f"- Relevant articles from top sources\n"
            f"- Strategic learning recommendations\n\n"
            f"The full digest is structured and ready for you to explore. "
            f"Would you like me to dive deeper into any specific aspect?"
        )
    
    def _classify_knowledge_intent(self, message: str) -> str:
        """Classify the type of knowledge request"""
        message_lower = message.lower()
        
        # Check for digest creation keywords
        digest_keywords = ["digest", "learn", "learning", "curate", "summary", "overview"]
        if any(kw in message_lower for kw in digest_keywords):
            return "create_digest"
        
        # Check for search keywords
        search_keywords = ["find", "search", "look up", "about", "research"]
        if any(kw in message_lower for kw in search_keywords):
            return "search_topic"
        
        return "general"
    
    def _extract_topic(self, message: str) -> str:
        """Extract the topic from a search query"""
        # Simplified extraction - in production use NLU
        message_lower = message.lower()
        
        # Remove common question words
        for word in ["find", "search", "about", "what is", "tell me about"]:
            message_lower = message_lower.replace(word, "")
        
        return message_lower.strip() or "general knowledge"
