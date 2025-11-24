"""
Personal Vibe CEO System - Agent Orchestrator
Handles agent routing and context switching
"""

import logging
from typing import Dict, Optional
from enum import Enum

# Import agents
from src.agents.vibe_agent import VibeAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.knowledge_agent import KnowledgeAgent

# Import tools
from src.tools.mock_tools import (
    get_calendar_service,
    get_search_service,
    get_todo_service
)

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent type enumeration"""
    VIBE = "vibe"
    PLANNER = "planner"
    KNOWLEDGE = "knowledge"


class Orchestrator:
    """
    Main orchestrator for routing messages to appropriate agents
    and managing conversation context
    """
    
    def __init__(self, db):
        """Initialize the orchestrator with agent instances"""
        self.db = db
        self.sessions = {}  # Session management
        
        # Initialize tool services
        self.calendar_service = get_calendar_service()
        self.search_service = get_search_service()
        self.todo_service = get_todo_service()
        
        # Initialize agents
        self.agents = {
            AgentType.VIBE.value: VibeAgent(db),
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
        
        logger.info("Orchestrator initialized with all agents")
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process incoming message and route to appropriate agent
        
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
            
            # Route to agent
            response = await self._route_to_agent(
                agent_type,
                user_id,
                message,
                session
            )
            
            # Update session context
            self._update_session(session, agent_type, message, response)
            
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
        # Currently only Vibe Agent has proactive capability
        vibe_agent = self.agents[AgentType.VIBE.value]
        return await vibe_agent.check_for_proactive_outreach(user_id)
    
    def _classify_intent(
        self,
        message: str,
        context: Optional[Dict] = None
    ) -> AgentType:
        """
        Classify user intent to determine which agent should respond
        
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
                return AgentType(pref)
        
        # Intent classification based on keywords
        message_lower = message.lower()
        
        # Planner keywords (highest priority for clear actions)
        planner_keywords = [
            "schedule", "calendar", "appointment", "book", "plan", 
            "reminder", "doctor", "dentist", "checkup", "task", "todo"
        ]
        if any(kw in message_lower for kw in planner_keywords):
            logger.info(f"Classified as PLANNER intent: {message[:50]}")
            return AgentType.PLANNER
        
        # Knowledge keywords
        knowledge_keywords = [
            "learn", "research", "find", "search", "digest", 
            "article", "topic", "study", "read about"
        ]
        if any(kw in message_lower for kw in knowledge_keywords):
            logger.info(f"Classified as KNOWLEDGE intent: {message[:50]}")
            return AgentType.KNOWLEDGE
        
        # Vibe keywords (emotional, health, well-being)
        vibe_keywords = [
            "feel", "stressed", "tired", "sleep", "balance", 
            "overwhelmed", "anxiety", "mood", "energy", "health"
        ]
        if any(kw in message_lower for kw in vibe_keywords):
            logger.info(f"Classified as VIBE intent: {message[:50]}")
            return AgentType.VIBE
        
        # Default to Vibe for general conversation
        logger.info(f"Defaulting to VIBE for: {message[:50]}")
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
            "context": {}
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
        Route message to the appropriate agent
        
        Args:
            agent_type: Which agent to use
            user_id: User identifier
            message: User message
            session: Session context
            
        Returns:
            Agent response
        """
        logger.info(f"Routing to {agent_type.value} agent for user {user_id}")
        
        # Get the agent instance
        agent = self.agents.get(agent_type.value)
        
        if not agent:
            logger.error(f"Agent not found: {agent_type.value}")
            return {
                "agent_type": "error",
                "response": "Internal error: agent not available",
                "timestamp": "",
                "metadata": {}
            }
        
        # Process message with the agent
        context = session.get("context", {})
        response = await agent.process_message(user_id, message, context)
        
        return response

