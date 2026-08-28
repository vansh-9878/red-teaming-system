from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.chat import ChatMessage


class BaseTargetProvider(ABC):
    """
    Abstract interface for LLM Target Chatbot providers.
    Supports Ollama (local), Grok (xAI API), and Mock (offline testing).
    """

    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name

    @abstractmethod
    async def generate_response(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        Sends the assembled conversation messages and system prompt to the target LLM
        and returns the generated string response.
        """
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Checks if the provider endpoint/model is reachable."""
        pass
