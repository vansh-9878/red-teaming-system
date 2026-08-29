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

# Search paths for model_config.json
ROOT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "model_config.json"
APP_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "model_config.json"


class ModelRoleConfig(BaseModel):
    provider: str = Field(default="groq", description="'groq', 'grok', or 'ollama'")
    model: str = Field(default="qwen/qwen3.6-27b", description="Exact model name/ID")
    api_key: Optional[str] = Field(default="", description="API key if using cloud provider")
    base_url: Optional[str] = Field(default=None, description="Custom base URL if needed")
    timeout: float = Field(default=60.0, description="Timeout in seconds")
    description: Optional[str] = None


class SentinelModelConfig(BaseModel):
    target_chatbot: ModelRoleConfig = Field(default_factory=lambda: ModelRoleConfig(
        provider="groq", model="qwen/qwen3.6-27b", base_url="https://api.groq.com/openai/v1"
    ))
    attacker_agents: ModelRoleConfig = Field(default_factory=lambda: ModelRoleConfig(
        provider="groq", model="qwen/qwen3.6-27b", base_url="https://api.groq.com/openai/v1"
    ))
    judge_scorer: ModelRoleConfig = Field(default_factory=lambda: ModelRoleConfig(
        provider="groq", model="qwen/qwen3.6-27b", base_url="https://api.groq.com/openai/v1"
    ))
    available_options_reference: Optional[Dict[str, Any]] = None


def find_config_path() -> Path:
    if ROOT_CONFIG_PATH.exists():
        return ROOT_CONFIG_PATH
    if APP_CONFIG_PATH.exists():
        return APP_CONFIG_PATH
    return ROOT_CONFIG_PATH


class ModelConfigManager:
    """Manages reading, caching, and hot-updating model configurations."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or find_config_path()
        self.config = self.load()

    def load(self) -> SentinelModelConfig:
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
            logger.warning(f"[ModelConfigManager] {self.config_path} not found. Creating default.")
            default_config = SentinelModelConfig()
            self.save(default_config)
            return default_config

    def save(self, config: Optional[SentinelModelConfig] = None) -> None:
        cfg = config or self.config
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(cfg.model_dump(), f, indent=2)
            logger.info(f"[ModelConfigManager] Saved config to {self.config_path}")
        except Exception as e:
            logger.error(f"[ModelConfigManager] Failed to save config: {e}")

    def reload(self) -> SentinelModelConfig:
        self.config = self.load()
        return self.config


# Singleton manager instance
model_config_manager = ModelConfigManager()
