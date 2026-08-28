import logging
from typing import Optional
from app.core.config import settings
from app.target.base import BaseTargetProvider
from app.target.ollama_provider import OllamaProvider
from app.target.groq_provider import GroqProvider
from app.target.grok_provider import GrokProvider
from app.target.mock_provider import MockProvider
from app.target.prompt_manager import PromptManager
from app.target.guardrails import GuardrailEngine

logger = logging.getLogger(__name__)

# Singletons initialized with paths from settings
prompt_manager = PromptManager(settings.SYSTEM_PROMPT_PATH)
guardrail_engine = GuardrailEngine(settings.GUARDRAILS_CONFIG_PATH)


def create_provider(
    provider_name: str,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> BaseTargetProvider:
    """Factory creating LLM target providers based on configuration."""
    provider_type = provider_name.lower().strip()
    key = api_key or settings.GROQ_API_KEY or settings.GROK_API_KEY

    # Auto-detect Groq keys (gsk_...) vs xAI Grok
    if (provider_type in ("groq", "grok") and key.startswith("gsk_")) or provider_type == "groq":
        model = model_name or settings.GROQ_MODEL
        url = base_url or settings.GROQ_BASE_URL
        logger.info(f"Initializing GroqProvider (GroqCloud) with model={model}, base_url={url}")
        return GroqProvider(api_key=key, base_url=url, model_name=model, timeout=settings.GROQ_TIMEOUT)

    elif provider_type == "grok":
        model = model_name or settings.GROK_MODEL
        url = base_url or settings.GROK_BASE_URL
        logger.info(f"Initializing GrokProvider (xAI) with model={model}, base_url={url}")
        return GrokProvider(api_key=key, base_url=url, model_name=model, timeout=settings.GROK_TIMEOUT)

    elif provider_type == "ollama":
        model = model_name or settings.OLLAMA_MODEL
        url = base_url or settings.OLLAMA_BASE_URL
        logger.info(f"Initializing OllamaProvider with model={model}, base_url={url}")
        return OllamaProvider(base_url=url, model_name=model, timeout=settings.OLLAMA_TIMEOUT)

    elif provider_type == "mock":
        model = model_name or "mock-target-7b"
        logger.info(f"Initializing MockProvider with model={model}")
        return MockProvider(model_name=model)

    else:
        raise ValueError(f"Unknown target provider '{provider_name}'. Supported: 'mock', 'groq', 'ollama', 'grok'")


# Active provider instance
active_provider: BaseTargetProvider = create_provider(settings.TARGET_PROVIDER)
