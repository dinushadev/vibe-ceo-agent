"""
Personal Vibe CEO System - Agent Orchestrator
Handles agent routing and context switching with ADK-powered agents
"""

import logging
from typing import Dict, Optional
from enum import Enum

# Import ADK-powered agents
from src.agents.vibe_agent import VibeAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.knowledge_agent import KnowledgeAgent

# Import tools (for backward compatibility)
from src.tools.mock_tools import (
    get_calendar_service,
    get_search_service,
    get_todo_service
)

# Import memory service
from src.memory.memory_service import get_memory_service

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent type enumeration"""
    VIBE = "vibe"
    PLANNER = "planner"
    KNOWLEDGE = "knowledge"


class Orchestrator:
    """
    Main orchestrator for routing messages to appropriate ADK agents
    and managing conversation context
    """
    
    def __init__(self, db):
        """Initialize the orchestrator with ADK agent instances"""
        self.db = db
        self.sessions = {}  # Session management
        
        # Initialize memory service for all agents
        self.memory_service = get_memory_service(db)
        
        # Initialize tool services (for backward compatibility)
        self.calendar_service = get_calendar_service()
        self.search_service = get_search_service()
        self.todo_service = get_todo_service()
        
        # Initialize ADK-powered agents
        try:
            self.agents = {
                AgentType.VIBE.value: VibeAgent(db, self.memory_service),
                AgentType.PLANNER.value: PlannerAgent(
                    db,
                    self.calendar_service,
                    self.todo_service
                ),
                AgentType.KNOWLEDGE.value: KnowledgeAgent(
                    db,
                    self.search_service
                )
            }
            logger.info("Orchestrator initialized with ADK-powered agents")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process incoming message and route to appropriate ADK agent
        
        Args:
            user_id: User identifier
            message: User message
            context: Optional context with agent preference and session info
            
        Returns:
            Agent response with metadata
        """
        try:
            # Determine which agent should handle the message
            agent_type = self._classify_intent(message, context)
            
            # Get or create session
            session_id = context.get("session_id") if context else None
            session = self._get_session(user_id, session_id)
            
            # Route to ADK agent
            response = await self._route_to_agent(
                agent_type,
                user_id,
                message,
                session
            )
            
            # Update session context
            self._update_session(session, agent_type, message, response)
            
            logger.info(
                f"Processed message for user {user_id} with {agent_type.value} agent "
                f"(latency: {response.get('metadata', {}).get('latency_ms', 'N/A')}ms)"
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "agent_type": "error",
                "response": "I encountered an issue processing your request. Please try again.",
                "timestamp": "",
                "metadata": {"error": str(e)}
            }
    
    async def check_proactive_triggers(self, user_id: str) -> Optional[Dict]:
        """
        Check if any agent should proactively reach out (FR1)
        
        Args:
            user_id: User identifier
            
        Returns:
            Proactive message if triggered, None otherwise
        """
        try:
            # Currently only Vibe Agent has proactive capability
            vibe_agent = self.agents[AgentType.VIBE.value]
            proactive_message = await vibe_agent.check_for_proactive_outreach(user_id)
            
            if proactive_message:
                logger.info(f"Proactive message triggered for user {user_id}")
            
            return proactive_message
            
        except Exception as e:
            logger.error(f"Error checking proactive triggers: {e}", exc_info=True)
            return None
    
    def _classify_intent(
        self,
        message: str,
        context: Optional[Dict] = None
    ) -> AgentType:
        """
        Classify user intent to determine which agent should respond
        
        Uses keyword-based classification. In a more advanced implementation,
        this could use an LLM-based classifier or ADK's routing capabilities.
        
        Args:
            message: User message
            context: Optional context
            
        Returns:
            AgentType to handle the message
        """
        # Check for explicit agent preference in context
        if context and "agent_preference" in context:
            pref = context["agent_preference"]
            if pref in ["vibe", "planner", "knowledge"]:
                logger.info(f"Using explicit agent preference: {pref}")
                return AgentType(pref)
        
        # Intent classification based on keywords
        message_lower = message.lower()
        
        # Planner keywords (highest priority for clear actions)
        planner_keywords = [
            "schedule", "calendar", "appointment", "book", "plan", 
            "reminder", "doctor", "dentist", "checkup", "task", "todo",
            "meeting", "event", "when", "available"
        ]
        if any(kw in message_lower for kw in planner_keywords):
            logger.info(f"Classified as PLANNER intent: {message[:50]}...")
            return AgentType.PLANNER
        
        # Knowledge keywords
        knowledge_keywords = [
            "learn", "research", "find", "search", "digest", 
            "article", "topic", "study", "read about", "teach",
            "explain", "what is", "how does", "information"
        ]
        if any(kw in message_lower for kw in knowledge_keywords):
            logger.info(f"Classified as KNOWLEDGE intent: {message[:50]}...")
            return AgentType.KNOWLEDGE
        
        # Vibe keywords (emotional, health, well-being)
        vibe_keywords = [
            "feel", "stressed", "tired", "sleep", "balance", 
            "overwhelmed", "anxiety", "mood", "energy", "health",
            "burnout", "rest", "wellbeing", "wellness"
        ]
        if any(kw in message_lower for kw in vibe_keywords):
            logger.info(f"Classified as VIBE intent: {message[:50]}...")
            return AgentType.VIBE
        
        # Default to Vibe for general conversation
        logger.info(f"Defaulting to VIBE for general conversation: {message[:50]}...")
        return AgentType.VIBE
    
    def _get_session(self, user_id: str, session_id: Optional[str]) -> Dict:
        """Get or create a session for the user"""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        # Create new session
        new_session = {
            "user_id": user_id,
            "history": [],
            "current_agent": None,
            "context": {},
            "created_at": None
        }
        
        if session_id:
            self.sessions[session_id] = new_session
        
        return new_session
    
    def _update_session(
        self,
        session: Dict,
        agent_type: AgentType,
        message: str,
        response: Dict
    ):
        """Update session with interaction history"""
        session["history"].append({
            "message": message,
            "agent": agent_type.value,
            "response": response,
            "timestamp": response.get("timestamp")
        })
        session["current_agent"] = agent_type.value
        
        # Keep only last 10 interactions to prevent memory bloat
        if len(session["history"]) > 10:
            session["history"] = session["history"][-10:]
    
    async def _route_to_agent(
        self,
        agent_type: AgentType,
        user_id: str,
        message: str,
        session: Dict
    ) -> Dict:
        """
        Route message to the appropriate ADK agent
        
        Args:
            agent_type: Which agent to use
            user_id: User identifier
            message: User message
            session: Session context
            
        Returns:
            Agent response with ADK metadata
        """
        logger.info(f"Routing to {agent_type.value} agent for user {user_id}")
        
        # Get the ADK agent instance
        agent = self.agents.get(agent_type.value)
        
        if not agent:
            logger.error(f"Agent not found: {agent_type.value}")
            return {
                "agent_type": "error",
                "response": "Internal error: agent not available",
                "timestamp": "",
                "metadata": {}
            }
        
        # Process message with the ADK agent
        context = session.get("context", {})
        response = await agent.process_message(user_id, message, context)
        
        # Log ADK usage
        if response.get("metadata", {}).get("adk_powered"):
            logger.info(f"ADK agent processed message successfully")
            if response["metadata"].get("tools_used"):
                logger.info(f"Tools used: {response['metadata']['tools_used']}")
        
        return response
    
    def get_agent_status(self) -> Dict:
        """
        Get status of all agents for observability
        
        Returns:
            Status information for all agents
        """
        status = {
            "total_agents": len(self.agents),
            "agents": {},
            "memory_service_active": self.memory_service is not None
        }
        
        for agent_type, agent in self.agents.items():
            status["agents"][agent_type] = {
                "type": agent_type,
                "adk_enabled": hasattr(agent, 'adk_agent') and agent.adk_agent is not None,
                "memory_enabled": agent.memory_service is not None
            }
        
        return status
