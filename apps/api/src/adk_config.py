"""
ADK Configuration and Initialization
Centralized configuration for Google Agent Development Kit
"""

import os
import logging
from typing import Optional, Dict, Any
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.cloud import aiplatform

logger = logging.getLogger(__name__)


class ADKConfig:
    """Centralized ADK configuration manager"""
    
    def __init__(self):
        """Initialize ADK configuration from environment variables"""
        # Google Cloud Configuration
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        # ADK Model Configuration
        self.model = os.getenv("ADK_MODEL", "gemini-2.0-flash-exp")
        self.temperature = float(os.getenv("ADK_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("ADK_MAX_TOKENS", "8192"))
        
        print('self.model', self.model)
        print('self.temperature', self.temperature)
        print('self.max_tokens', self.max_tokens)
        print('self.project_id', self.project_id)
        print('self.location', self.location)
        print('self.credentials_path', self.credentials_path)
        
        # Validate required configuration
        self._validate_config()
        
        # Initialize Vertex AI
        self._init_vertex_ai()
        
        logger.info(f"ADK Config initialized: project={self.project_id}, location={self.location}, model={self.model}")
    
    def _validate_config(self):
        """Validate required configuration is present"""
        if not self.project_id:
            logger.warning("GOOGLE_CLOUD_PROJECT not set - ADK agents may not work properly")
        
        if not self.credentials_path:
            logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set - using default credentials")
    
    def _init_vertex_ai(self):
        """Initialize Vertex AI client"""
        try:
            aiplatform.init(
                project=self.project_id,
                location=self.location
            )
            logger.info("Vertex AI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            logger.warning("ADK agents will be initialized but may fail at runtime without proper credentials")
    
    def get_model_config(self) -> Gemini:
        """Get model configuration for agent creation"""
        # Initialize Vertex AI model
        # Credentials are loaded from GOOGLE_APPLICATION_CREDENTIALS env var
        model = Gemini(
            model=self.model,
            vertexai=True,
            project=self.project_id,
            location=self.location,
            parameters={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens
            }
        )
        return model
    
    def create_agent(
        self,
        name: str,
        instruction: str,
        description: str,
        tools: Optional[list] = None,
        sub_agents: Optional[list] = None,
        **kwargs
    ) -> LlmAgent:
        """
        Create an ADK LlmAgent with standardized configuration
        
        Args:
            name: Agent name
            instruction: System instruction for the agent
            description: Agent description
            tools: List of tools the agent can use
            sub_agents: List of sub-agents (for multi-agent systems)
            **kwargs: Additional agent configuration
            
        Returns:
            Configured LlmAgent instance
        """
        agent_config = {
            "name": name,
            "model": self.get_model_config(),
            "instruction": instruction,
            "description": description,
            **kwargs
        }
        
        # Add optional parameters
        if tools:
            agent_config["tools"] = tools
        
        if sub_agents:
            agent_config["sub_agents"] = sub_agents
        
        try:
            agent = LlmAgent(**agent_config)
            logger.info(f"Created ADK agent: {name}")
            return agent
        except Exception as e:
            logger.error(f"Failed to create ADK agent '{name}': {e}")
            raise


# Global configuration instance
_adk_config: Optional[ADKConfig] = None


def get_adk_config() -> ADKConfig:
    """Get or create the global ADK configuration instance"""
    global _adk_config
    if _adk_config is None:
        _adk_config = ADKConfig()
    return _adk_config


def create_agent(
    name: str,
    instruction: str,
    description: str,
    tools: Optional[list] = None,
    sub_agents: Optional[list] = None,
    **kwargs
) -> LlmAgent:
    """
    Convenience function to create an ADK agent
    
    Args:
        name: Agent name
        instruction: System instruction
        description: Agent description
        tools: Optional list of tools
        sub_agents: Optional list of sub-agents
        **kwargs: Additional configuration
        
    Returns:
        Configured LlmAgent
    """
    config = get_adk_config()
    return config.create_agent(
        name=name,
        instruction=instruction,
        description=description,
        tools=tools,
        sub_agents=sub_agents,
        **kwargs
    )
