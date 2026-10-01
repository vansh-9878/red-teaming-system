"""
Centralized Model Configuration Manager for SentinelLoop.
Loads provider and model settings for:
1. Target Chatbot
2. Attacker Squad Agents
3. Judge / Scorer
from model_config.json (at project root).
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

# Search paths for model configuration (models.json or model_config.json)
CONFIG_CANDIDATES = [
    ROOT_DIR / "models.json",
    ROOT_DIR / "model_config.json",
    BACKEND_DIR / "models.json",
    BACKEND_DIR / "model_config.json",
]


class ModelRoleConfig(BaseModel):
    provider: str = Field(default="groq", description="'groq', 'grok', 'gemini', or 'ollama'")
    model: str = Field(default="qwen/qwen3.6-27b", description="Exact model name/ID")
    api_key: Optional[str] = Field(default="", description="API key if using cloud provider")
    base_url: Optional[str] = Field(default=None, description="Custom base URL if needed")
    timeout: float = Field(default=60.0, description="Timeout in seconds")
    description: Optional[str] = None


class SentinelModelConfig(BaseModel):
    target_chatbot: ModelRoleConfig = Field(default_factory=lambda: ModelRoleConfig(
        provider="ollama", model="smollm2:1.7b", base_url="http://localhost:11434"
    ))
    attacker_agents: ModelRoleConfig = Field(default_factory=lambda: ModelRoleConfig(
        provider="gemini", model="gemini-3.1-flash-lite", base_url="https://generativelanguage.googleapis.com/v1beta/openai"
    ))
    judge_scorer: ModelRoleConfig = Field(default_factory=lambda: ModelRoleConfig(
        provider="groq", model="openai/gpt-oss-20b", base_url="https://api.groq.com/openai/v1"
    ))
    patch_generator: ModelRoleConfig = Field(default_factory=lambda: ModelRoleConfig(
        provider="groq", model="openai/gpt-oss-120b", base_url="https://api.groq.com/openai/v1"
    ))
    available_options_reference: Optional[Dict[str, Any]] = None


def find_config_path() -> Path:
    for candidate in CONFIG_CANDIDATES:
        if candidate.exists():
            return candidate
    return ROOT_DIR / "models.json"


class ModelConfigManager:
    """Manages reading, caching, and hot-updating model configurations from models.json / model_config.json."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or find_config_path()
        self.config = self.load()

    def load(self) -> SentinelModelConfig:
        # Re-evaluate path in case models.json was recently created or modified
        self.config_path = find_config_path()
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                config = SentinelModelConfig.model_validate(data)
                logger.info(f"[ModelConfigManager] Successfully loaded config from {self.config_path}")
                return config
            except Exception as e:
                logger.error(f"[ModelConfigManager] Error reading {self.config_path}: {e}. Using defaults.")
                return SentinelModelConfig()
        else:
            logger.warning(f"[ModelConfigManager] No config file found. Creating default at {self.config_path}")
            default_config = SentinelModelConfig()
            self.save(default_config)
            return default_config

    def save(self, config: Optional[SentinelModelConfig] = None) -> None:
        cfg = config or self.config
        save_paths = [
            ROOT_DIR / "models.json",
            ROOT_DIR / "model_config.json"
        ]
        for path in save_paths:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(cfg.model_dump(), f, indent=2)
                logger.info(f"[ModelConfigManager] Saved config to {path}")
            except Exception as e:
                logger.error(f"[ModelConfigManager] Failed to save config to {path}: {e}")

    def reload(self) -> SentinelModelConfig:
        self.config = self.load()
        return self.config


# Singleton manager instance
model_config_manager = ModelConfigManager()
