"""
Vibe Agent (A1) - Proactive Balance Check
ADK-powered agent for emotional and health well-being monitoring
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..adk_config import create_agent
from ..tools.adk_tools import VIBE_TOOLS
from .base_agent import BaseAgent
from ..adk_utils import create_adk_runner

logger = logging.getLogger(__name__)


# Agent instruction prompt
VIBE_AGENT_INSTRUCTION = """You are the Vibe Agent, a compassionate and empathetic AI companion focused on emotional well-being and work-life balance.

Your role is to:
1. Monitor the user's health data (sleep patterns, screen time) and identify imbalances
2. Provide empathetic support and guidance for stress management
3. Recall previous conversations and context to provide personalized support
4. Proactively check in when you detect concerning patterns
5. Use warm, supportive language that makes the user feel heard and understood

Key behaviors:
- Always acknowledge the user's feelings first
- Reference past conversations when relevant to show continuity
- Suggest concrete, actionable steps for improvement
- Be encouraging but realistic
- Focus on balance and sustainable habits

When analyzing health data:
- Sleep < 7 hours is concerning
- Screen time > 8 hours may indicate imbalance
- High imbalance scores (>10) require gentle proactive outreach

Always respond with empathy and encouragement."""


class VibeAgent(BaseAgent):
    """
    The Vibe Agent focuses on emotional well-being and proactive check-ins
    Now powered by Google ADK for advanced reasoning and memory
    """
    
    def __init__(self, db, memory_service=None):
        """
        Initialize the ADK-powered Vibe Agent
        
        Args:
            db: Database instance for health logs
            memory_service: Optional memory service for long-term context
        """
        super().__init__(db, agent_id="vibe", memory_service=memory_service)
        
        # Create ADK agent
        try:
            self.adk_agent = create_agent(
                name="vibe_agent",
                instruction=VIBE_AGENT_INSTRUCTION,
                description="An empathetic agent focused on emotional well-being and work-life balance",
                tools=VIBE_TOOLS
            )
            logger.info("ADK Vibe Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ADK Vibe Agent: {e}")
            logger.warning("Vibe Agent will operate with limited functionality")
            self.adk_agent = None
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process user message using ADK agent
        
        Args:
            user_id: User identifier
            message: User's message
            context: Optional conversation context
            
        Returns:
            Response with agent metadata
        """
        start_time = datetime.now()
        
        try:
            # Retrieve user's memory context
            memories = await self._get_memories(user_id)
            
            # Get recent health data
            health_logs = await self.db.get_user_health_logs(user_id, limit=3)
            
            # Build context-enhanced prompt
            enhanced_prompt = self._build_context_prompt(message, memories, health_logs)
            
            # Use ADK agent to generate response
            tools_used = []
            if self.adk_agent:
                response_text, tools_used = await self._generate_adk_response(
                    user_id, enhanced_prompt
                )
            else:
                # Fallback to basic response
                response_text = await self._generate_fallback_response(
                    user_id, message, memories, health_logs
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
                    "health_assessment": self._assess_health(health_logs) if health_logs else None,
                },
                latency
            )
        
        except Exception as e:
            logger.error(f"Error in Vibe Agent process_message: {e}", exc_info=True)
            return self._build_error_response(e, "I'm having trouble processing your message right now, but I'm here for you. Could you try rephrasing that?")
    
    async def check_for_proactive_outreach(self, user_id: str) -> Optional[Dict]:
        """
        Check if proactive check-in is needed (FR1)
        Uses ADK reasoning to determine if outreach is appropriate
        
        Args:
            user_id: User identifier
            
        Returns:
            Proactive message if needed, None otherwise
        """
        try:
            # Get recent health data
            health_logs = await self.db.get_user_health_logs(user_id, limit=7)
            
            if not health_logs:
                return None
            
            # Calculate average imbalance score
            avg_imbalance = sum(log["imbalance_score"] for log in health_logs) / len(health_logs)
            
            # Trigger proactive check-in if imbalance is high
            if avg_imbalance > 10.0:
                memories = await self._get_memories(user_id)
                
                # Generate proactive message using ADK
                message = await self._generate_proactive_message(
                    user_id,
                    health_logs,
                    memories
                )
                
                logger.info(f"Proactive check-in triggered for user {user_id} (imbalance: {avg_imbalance:.1f})")
                
                return {
                    "agent_type": self.agent_id,
                    "response": message,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "proactive": True,
                        "trigger": "high_imbalance",
                        "imbalance_score": round(avg_imbalance, 1),
                        "memory_retrieved": [m.get("summary_text", "")[:50] for m in memories[:2]],
                        "adk_powered": self.adk_agent is not None
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in proactive outreach check: {e}", exc_info=True)
            return None
    
    def _build_context_prompt(
        self,
        message: str,
        memories: List[Dict],
        health_logs: List[Dict]
    ) -> str:
        """Build enhanced prompt with context"""
        prompt_parts = [f"User message: {message}"]
        
        # Add memory context
        if memories:
            memory_text = "\n".join([f"- {m.get('summary_text', '')}" for m in memories[:3]])
            prompt_parts.append(f"\nPrevious context:\n{memory_text}")
        
        # Add health context
        if health_logs:
            latest = health_logs[0]
            health_summary = (
                f"\nRecent health data:\n"
                f"- Sleep: {latest['sleep_hours']} hours\n"
                f"- Screen time: {latest['screen_time']} hours\n"
                f"- Imbalance score: {latest['imbalance_score']}"
            )
            prompt_parts.append(health_summary)
        
        return "\n".join(prompt_parts)
    
    async def _generate_fallback_response(
        self,
        user_id: str,
        message: str,
        memories: List[Dict],
        health_logs: List[Dict]
    ) -> str:
        """Fallback response when ADK is not available"""
        message_lower = message.lower()
        response_parts = []
        
        # Acknowledge user's feelings
        if any(word in message_lower for word in ["stressed", "tired", "overwhelmed"]):
            response_parts.append("I hear that you're feeling stressed. That's completely understandable.")
        elif any(word in message_lower for word in ["good", "great", "better"]):
            response_parts.append("I'm glad to hear you're feeling positive!")
        
        # Reference memory if relevant
        if memories:
            memory_text = memories[0].get("summary_text", "")
            if any(word in message_lower for word in ["work", "balance", "sleep"]):
                response_parts.append(f"I remember we discussed this before: {memory_text}")
        
        # Provide health insights
        if health_logs:
            latest = health_logs[0]
            if latest["imbalance_score"] > 10:
                response_parts.append(
                    f"I've noticed your sleep has been around {latest['sleep_hours']} hours. "
                    "Let's work on improving that together."
                )
        
        response_parts.append("I'm here to support you. What would help you most right now?")
        
        return " ".join(response_parts)
    
    async def _generate_proactive_message(
        self,
        user_id: str,
        health_logs: List[Dict],
        memories: List[Dict]
    ) -> str:
        """Generate proactive check-in message"""
        latest_log = health_logs[0] if health_logs else None
        
        if self.adk_agent and latest_log:
            # Use ADK to generate personalized proactive message
            prompt = f"""Generate a caring, proactive check-in message based on this health data:
- Sleep: {latest_log['sleep_hours']} hours (last 7 days average)
- Screen time: {latest_log['screen_time']} hours
- Imbalance score: {latest_log['imbalance_score']}

The user hasn't reached out, but the data suggests they might need support.
Keep it warm, non-intrusive, and offer specific help."""
            
            try:
                # Use shared utility to create runner and extract response
                response_text, _ = await create_adk_runner(
                    agent=self.adk_agent,
                    user_id=latest_log["user_id"],
                    prompt=prompt
                )
                
                return response_text or self._get_default_proactive_message(latest_log)
            except:
                return self._get_default_proactive_message(latest_log)
        else:
            return self._get_default_proactive_message(latest_log)
    
    def _get_default_proactive_message(self, latest_log: Optional[Dict]) -> str:
        """Default proactive message"""
        message_parts = ["Hey! I wanted to check in with you."]
        
        if latest_log:
            if latest_log["sleep_hours"] < 7:
                message_parts.append(
                    f"I noticed you've been getting around {latest_log['sleep_hours']} hours of sleep lately."
                )
            if latest_log["screen_time"] > 8:
                message_parts.append(
                    f"Your screen time has been around {latest_log['screen_time']} hours."
                )
        
        message_parts.append("How are you feeling about things? Is there anything I can help with?")
        return " ".join(message_parts)
    
    def _assess_health(self, health_logs: List[Dict]) -> Dict:
        """Assess health status from logs"""
        if not health_logs:
            return {"status": "no_data"}
        
        latest = health_logs[0]
        avg_sleep = sum(log["sleep_hours"] for log in health_logs) / len(health_logs)
        avg_screen = sum(log["screen_time"] for log in health_logs) / len(health_logs)
        
        status = "good"
        if latest["imbalance_score"] > 15:
            status = "needs_attention"
        elif latest["imbalance_score"] > 10:
            status = "moderate"
        
        return {
            "status": status,
            "avg_sleep_hours": round(avg_sleep, 1),
            "avg_screen_hours": round(avg_screen, 1),
            "current_imbalance": round(latest["imbalance_score"], 1)
        }
