import os
import time
from groq import Groq
from typing import Dict, Any, Optional, Generator
from src.core.llm_provider import LLMProvider

class GroqProvider(LLMProvider):
    def __init__(self, model_name: str = "qwen/qwen3-32b", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.client = Groq(api_key=self.api_key)
        self.model = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        # Build messages with system prompt if provided
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Groq usage data is in response.usage
        content = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "groq"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        # Build messages with system prompt if provided
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
