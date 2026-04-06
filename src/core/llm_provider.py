import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Generator

class LLMProvider(ABC):
    """
    Abstract Base Class for LLM Providers.
    Supports OpenAI, Google Gemini, Groq, and Local models.
    """

    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key

    def get_provider_info(self) -> Dict[str, str]:
        """
        Get information about the current LLM provider.
        
        Returns:
            Dict with provider name, model name, and type
        """
        return {
            "provider": self.__class__.__name__,
            "model": self.model_name,
            "type": self._get_provider_type()
        }
    
    def _get_provider_type(self) -> str:
        """Get provider type (openai, gemini, groq, local)"""
        class_name = self.__class__.__name__
        if "OpenAI" in class_name:
            return "openai"
        elif "Gemini" in class_name:
            return "gemini"
        elif "Groq" in class_name:
            return "groq"
        elif "Local" in class_name:
            return "local"
        return "unknown"

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Produce a non-streaming completion.
        Returns:
            Dict containing:
            - content: The response text
            - usage: { 'prompt_tokens', 'completion_tokens' }
            - latency_ms: Response time
        """
        pass

    @abstractmethod
    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Produce a streaming completion."""
        pass
