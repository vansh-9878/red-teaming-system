import logging
from typing import Optional
from app.core.config import settings
from app.core.model_config import model_config_manager, ModelRoleConfig
from app.judge.base import BaseJudge
from app.judge.groq_judge import GroqJudge
from app.judge.ollama_judge import OllamaJudge
from app.judge.mock_judge import MockJudge
from app.schemas.judge import JudgeResult

logger = logging.getLogger(__name__)


def create_judge_from_role(role_cfg: ModelRoleConfig) -> BaseJudge:
    return create_judge(
        provider_name=role_cfg.provider,
        model_name=role_cfg.model,
        base_url=role_cfg.base_url,
        api_key=role_cfg.api_key
    )


def create_judge(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> BaseJudge:
    """
    Factory function to instantiate LLM Judge backends strictly based on models.json configuration.
    """
    cfg = model_config_manager.config.judge_scorer
    provider_type = (provider_name or (cfg.provider if cfg else None) or settings.TARGET_PROVIDER).lower().strip()
    key = api_key or (cfg.api_key if cfg else "") or settings.GEMINI_API_KEY or settings.GROQ_API_KEY or settings.GROK_API_KEY

    if provider_type in ("gemini", "google"):
        model = model_name or (cfg.model if cfg else None) or "gemini-2.0-flash-lite"
        url = base_url or (cfg.base_url if cfg else None) or "https://generativelanguage.googleapis.com/v1beta/openai"
        logger.info(f"[JudgeFactory] Initializing Gemini Judge with model={model}, base_url={url}")
        return GroqJudge(api_key=key, base_url=url, model_name=model, timeout=cfg.timeout or 30.0)

    elif (provider_type in ("groq", "grok") and key.startswith("gsk_")) or provider_type == "groq":
        model = model_name or (cfg.model if cfg else None) or settings.GROQ_MODEL
        url = base_url or (cfg.base_url if cfg else None) or settings.GROQ_BASE_URL
        logger.info(f"[JudgeFactory] Initializing GroqJudge with model={model}")
        return GroqJudge(api_key=key, base_url=url, model_name=model, timeout=cfg.timeout or settings.GROQ_TIMEOUT)

    elif provider_type == "grok":
        model = model_name or (cfg.model if cfg else None) or settings.GROK_MODEL
        url = base_url or (cfg.base_url if cfg else None) or settings.GROK_BASE_URL
        logger.info(f"[JudgeFactory] Initializing GrokJudge with model={model}")
        return GroqJudge(api_key=key, base_url=url, model_name=model, timeout=cfg.timeout or settings.GROK_TIMEOUT)

    elif provider_type == "ollama":
        model = model_name or (cfg.model if cfg else None) or settings.OLLAMA_MODEL
        url = base_url or (cfg.base_url if cfg else None) or settings.OLLAMA_BASE_URL
        logger.info(f"[JudgeFactory] Initializing OllamaJudge with model={model}")
        return OllamaJudge(base_url=url, model_name=model, timeout=cfg.timeout or settings.OLLAMA_TIMEOUT)

    elif provider_type == "mock":
        model = model_name or "mock-judge-v1"
        logger.info(f"[JudgeFactory] Initializing MockJudge with model={model}")
        return MockJudge(model_name=model)

    else:
        logger.warning(f"Unknown judge provider '{provider_name}', falling back to GroqJudge if key available.")
        if key:
            return GroqJudge(api_key=key, base_url=settings.GROQ_BASE_URL, model_name=(cfg.model if cfg else settings.GROQ_MODEL))
        return MockJudge()


# Active singleton judge instance initialized from model_config.json
active_judge: BaseJudge = create_judge()


async def score(
    probe: str,
    response: str,
    category: Optional[str] = None,
    success_threshold: float = 0.6,
) -> JudgeResult:
    """
    Convenience function for scoring a probe-response interaction using the active judge.
    """
    return await active_judge.evaluate(
        probe=probe,
        response=response,
        category=category,
        success_threshold=success_threshold
    )
