import time
from typing import Any, Dict, Generator, Optional

from google import genai

from src.core.llm_provider import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(
        self, model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None
    ):
        super().__init__(model_name, api_key)
        # The new SDK uses a Client object
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def generate(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()

        # The new SDK has a dedicated system_instruction parameter
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={"system_instruction": system_prompt} if system_prompt else None,
        )

        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "content": response.text,
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            },
            "latency_ms": latency_ms,
            "provider": "google",
        }

    def stream(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        # stream_generate_content is the method for streaming
        responses = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=prompt,
            config={"system_instruction": system_prompt} if system_prompt else None,
        )

        for chunk in responses:
            yield chunk.text
