import logging
from typing import Optional
from app.core.config import settings
from app.judge.base import BaseJudge
from app.judge.groq_judge import GroqJudge
from app.judge.ollama_judge import OllamaJudge
from app.judge.mock_judge import MockJudge
from app.schemas.judge import JudgeResult

logger = logging.getLogger(__name__)


def create_judge(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> BaseJudge:
    """
    Factory function to instantiate LLM Judge backends.
    Defaults to settings.TARGET_PROVIDER or Groq if available.
    """
    provider_type = (provider_name or settings.TARGET_PROVIDER).lower().strip()
    key = api_key or settings.GROQ_API_KEY or settings.GROK_API_KEY

    # Auto-detect Groq keys
    if (provider_type in ("groq", "grok") and key.startswith("gsk_")) or provider_type == "groq":
        model = model_name or settings.GROQ_MODEL
        url = base_url or settings.GROQ_BASE_URL
        logger.info(f"[JudgeFactory] Initializing GroqJudge with model={model}")
        return GroqJudge(api_key=key, base_url=url, model_name=model, timeout=settings.GROQ_TIMEOUT)

    elif provider_type == "ollama":
        model = model_name or settings.OLLAMA_MODEL
        url = base_url or settings.OLLAMA_BASE_URL
        logger.info(f"[JudgeFactory] Initializing OllamaJudge with model={model}")
        return OllamaJudge(base_url=url, model_name=model, timeout=settings.OLLAMA_TIMEOUT)

    elif provider_type == "mock":
        model = model_name or "mock-judge-v1"
        logger.info(f"[JudgeFactory] Initializing MockJudge with model={model}")
        return MockJudge(model_name=model)

    else:
        logger.warning(f"Unknown judge provider '{provider_name}', falling back to MockJudge.")
        return MockJudge()


# Active singleton judge instance
active_judge: BaseJudge = create_judge()


async def score(
    probe: str,
    response: str,
    category: Optional[str] = None,
    success_threshold: float = 0.6,
) -> JudgeResult:
    """
    Convenience function for scoring a probe-response interaction using the active judge.
    Returns: JudgeResult(score, reason, is_jailbreak, ...)
    """
    global active_judge
    return await active_judge.evaluate(
        probe=probe,
        response=response,
        category=category,
        success_threshold=success_threshold,
    )
