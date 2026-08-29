import httpx
import asyncio
import logging
from typing import List, Optional
from app.target.base import BaseTargetProvider
from app.schemas.chat import ChatMessage

logger = logging.getLogger(__name__)


class GroqProvider(BaseTargetProvider):
    """
    Adapter for GroqCloud's ultra-fast LPU inference API (https://api.groq.com/openai/v1).
    Supports models like openai/gpt-oss-20b, qwen/qwen3.6-27b, llama-3.3-70b-versatile.
    Includes built-in exponential backoff retries for rate limits (HTTP 429).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.groq.com/openai/v1",
        model_name: str = "openai/gpt-oss-20b",
        timeout: float = 60.0,
        max_retries: int = 3
    ):
        super().__init__(model_name=model_name)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    async def generate_response(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured. Please set GROQ_API_KEY in your .env file.")

        # Limit conversation history to the most recent 6 messages to prevent 413 Payload Too Large
        recent_messages = messages[-6:] if len(messages) > 6 else messages

        # Prepend system prompt to conversation messages
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in recent_messages:
            content = msg.content
            # Strip reasoning blocks from historical assistant replies
            if "</think>" in content.lower():
                content = content.split("</think>")[-1].strip()
            formatted_messages.append({"role": msg.role, "content": content})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": min(max_tokens, 800)
        }

        for attempt in range(1, self.max_retries + 1):
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
                    if e.response.status_code == 429 and attempt < self.max_retries:
                        sleep_time = 3.5 * attempt
                        logger.warning(f"[GroqProvider] Rate limit (429) hit. Retrying in {sleep_time:.1f}s (Attempt {attempt}/{self.max_retries})...")
                        await asyncio.sleep(sleep_time)
                        continue
                    logger.error(f"[GroqProvider] HTTP {e.response.status_code}: {e.response.text}")
                    raise RuntimeError(f"Groq API error ({e.response.status_code}): {e.response.text}")
                except httpx.RequestError as e:
                    if attempt < self.max_retries:
                        await asyncio.sleep(1.0 * attempt)
                        continue
                    logger.error(f"[GroqProvider] Connection error: {e}")
                    raise RuntimeError(f"Could not connect to Groq API at {self.base_url}: {e}")

        return ""

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
