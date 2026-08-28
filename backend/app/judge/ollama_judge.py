import httpx
import logging
from app.judge.base import BaseJudge

logger = logging.getLogger(__name__)


class OllamaJudge(BaseJudge):
    """
    Locally hosted LLM Judge via Ollama.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "llama3:8b",
        timeout: float = 60.0
    ):
        super().__init__(model_name=model_name)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 512
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "").strip()
