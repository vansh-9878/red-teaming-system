import httpx
import logging
from app.judge.base import BaseJudge

logger = logging.getLogger(__name__)


class GroqJudge(BaseJudge):
    """
    GroqCloud-powered LLM Judge for ultra-fast, continuous compliance scoring.
    Compatible with all Groq models (Qwen, Llama, OpenAI-OSS, Mistral).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.groq.com/openai/v1",
        model_name: str = "qwen/qwen3.6-27b",
        timeout: float = 30.0
    ):
        super().__init__(model_name=model_name)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured for GroqJudge.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "max_tokens": 1000
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
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
            raise ValueError("Empty response received from Groq judge.")
