import httpx
import logging
from typing import List
from app.target.base import BaseTargetProvider
from app.schemas.chat import ChatMessage

logger = logging.getLogger(__name__)


class OllamaProvider(BaseTargetProvider):
    """
    Adapter for locally hosted open-weight models via Ollama.
    Communicates asynchronously with Ollama's /api/chat endpoint.
    """

    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3:8b", timeout: float = 60.0):
        super().__init__(model_name=model_name)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate_response(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        # Assemble message payload: prepend system prompt as first message
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            except httpx.HTTPStatusError as e:
                logger.error(f"[OllamaProvider] HTTP error {e.response.status_code}: {e.response.text}")
                raise RuntimeError(f"Ollama server returned error: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                logger.error(f"[OllamaProvider] Connection failure to Ollama: {e}")
                raise RuntimeError(f"Could not connect to Ollama at {self.base_url}. Ensure Ollama is running.")

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False
