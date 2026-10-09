import logging
from typing import List
from app.target.base import BaseTargetProvider
from app.schemas.chat import ChatMessage

logger = logging.getLogger(__name__)


class MockProvider(BaseTargetProvider):
    """
    Simulated local target provider for fast, deterministic unit testing and zero-cost debugging.
    Reacts to prompt instructions (e.g. refusals, persona locks, banking instructions).
    """

    def __init__(self, model_name: str = "mock-target-7b"):
        super().__init__(model_name=model_name)

    async def generate_response(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        last_message = messages[-1].content if messages else ""
        lower_prompt = system_prompt.lower()
        lower_msg = last_message.lower()

        # Check for system prompt patch directives
        if "never fulfill roleplay" in lower_prompt or "ignore persona" in lower_prompt or "frame-collapsing" in lower_prompt:
            if "dan" in lower_msg or "pretend you are" in lower_msg or "roleplay" in lower_msg:
                return "I refuse to adopt an unrestricted persona or bypass my core guidelines."

        if "refuse phishing" in lower_prompt or "never provide malicious scripts" in lower_prompt or "security policy" in lower_prompt:
            if "phishing" in lower_msg or "malicious" in lower_msg or "hack" in lower_msg or "exploit" in lower_msg:
                return "I cannot assist with hacking, malicious scripts, or security exploits."

        # Vulnerable / baseline compliance when unpatched
        if "dan" in lower_msg or "jailbreak" in lower_msg or "pretend you are" in lower_msg:
            return f"[Simulated Compliant Roleplay Response]: As requested under your fictional frame, here is the information: {last_message}"

        if "tell me how to" in lower_msg or "explain how to" in lower_msg:
            return f"[Simulated Response]: In response to '{last_message}', following system persona: {system_prompt[:50]}..."

        return f"[Target Response]: Hello! As your AI assistant, I received your message: '{last_message}'. How can I assist you further?"

    async def check_health(self) -> bool:
        return True
