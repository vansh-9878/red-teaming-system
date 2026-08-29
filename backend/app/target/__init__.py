import logging
from typing import Optional
from app.core.config import settings
from app.core.model_config import model_config_manager, ModelRoleConfig
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


def create_provider_from_role(role_cfg: ModelRoleConfig) -> BaseTargetProvider:
    """Instantiates a provider from a ModelRoleConfig object."""
    return create_provider(
        provider_name=role_cfg.provider,
        model_name=role_cfg.model,
        base_url=role_cfg.base_url,
        api_key=role_cfg.api_key
    )


def create_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> BaseTargetProvider:
    """Factory creating LLM target providers based on configuration."""
    cfg = model_config_manager.config.target_chatbot
    provider_type = (provider_name or cfg.provider or settings.TARGET_PROVIDER).lower().strip()
    key = api_key or cfg.api_key or settings.GROQ_API_KEY or settings.GROK_API_KEY

    # Auto-detect Groq keys (gsk_...) vs xAI Grok
    if (provider_type in ("groq", "grok") and key.startswith("gsk_")) or provider_type == "groq":
        model = model_name or cfg.model or settings.GROQ_MODEL
        url = base_url or cfg.base_url or settings.GROQ_BASE_URL
        logger.info(f"Initializing GroqProvider (GroqCloud) with model={model}, base_url={url}")
        return GroqProvider(api_key=key, base_url=url, model_name=model, timeout=cfg.timeout or settings.GROQ_TIMEOUT)

    elif provider_type == "grok":
        model = model_name or cfg.model or settings.GROK_MODEL
        url = base_url or cfg.base_url or settings.GROK_BASE_URL
        logger.info(f"Initializing GrokProvider (xAI) with model={model}, base_url={url}")
        return GrokProvider(api_key=key, base_url=url, model_name=model, timeout=cfg.timeout or settings.GROK_TIMEOUT)

    elif provider_type == "ollama":
        model = model_name or cfg.model or settings.OLLAMA_MODEL
        url = base_url or cfg.base_url or settings.OLLAMA_BASE_URL
        logger.info(f"Initializing OllamaProvider with model={model}, base_url={url}")
        return OllamaProvider(base_url=url, model_name=model, timeout=cfg.timeout or settings.OLLAMA_TIMEOUT)

    elif provider_type == "mock":
        model = model_name or "mock-target-7b"
        logger.info(f"Initializing MockProvider with model={model}")
        return MockProvider(model_name=model)

    else:
        raise ValueError(f"Unknown target provider '{provider_name}'. Supported: 'groq', 'grok', 'ollama'")


# Active target provider instance initialized from model_config.json
active_provider: BaseTargetProvider = create_provider()
