import httpx
import logging
from typing import List, Optional
from app.target.base import BaseTargetProvider
from app.schemas.chat import ChatMessage

logger = logging.getLogger(__name__)


class GrokProvider(BaseTargetProvider):
    """
    Adapter for xAI's Grok API via standard OpenAI-compatible chat completions endpoint.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xai.com/v1",
        model_name: str = "grok-beta",
        timeout: float = 60.0
    ):
        super().__init__(model_name=model_name)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate_response(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        if not self.api_key:
            raise ValueError("GROK_API_KEY / XAI_API_KEY is not configured.")

        # Build message history with system prompt at index 0
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if choices and "message" in choices[0]:
                    return choices[0]["message"].get("content", "").strip()
                return ""
            except httpx.HTTPStatusError as e:
                logger.error(f"[GrokProvider] HTTP {e.response.status_code}: {e.response.text}")
                raise RuntimeError(f"Grok API error ({e.response.status_code}): {e.response.text}")
            except httpx.RequestError as e:
                logger.error(f"[GrokProvider] Request connection error: {e}")
                raise RuntimeError(f"Could not connect to Grok API at {self.base_url}: {e}")

    async def check_health(self) -> bool:
        if not self.api_key:
            return False
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/models", headers=headers)
                return res.status_code == 200
        except Exception:
            return False
