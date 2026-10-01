import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Active Provider: "mock", "groq", "ollama", or "grok"
    TARGET_PROVIDER: str = "groq"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Google Gemini Settings
    GEMINI_API_KEY: str = Field(default="", validation_alias="GEMINI_API_KEY")
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    GEMINI_MODEL: str = "gemini-2.0-flash-lite"
    GEMINI_TIMEOUT: float = 60.0

    # Groq (GroqCloud LPU) Settings (e.g. gsk_... keys)
    GROQ_API_KEY: str = Field(default="", validation_alias="GROQ_API_KEY")
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    GROQ_TIMEOUT: float = 60.0

    # xAI Grok Settings (e.g. xai-... keys)
    GROK_API_KEY: str = Field(default="", validation_alias="GROK_API_KEY")
    GROK_BASE_URL: str = "https://api.xai.com/v1"
    GROK_MODEL: str = "grok-beta"
    GROK_TIMEOUT: float = 60.0

    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    OLLAMA_TIMEOUT: float = 60.0

    # File paths for hot-reloading & patching
    SYSTEM_PROMPT_PATH: str = str(BASE_DIR / "app" / "core" / "system_prompt.txt")
    GUARDRAILS_CONFIG_PATH: str = str(BASE_DIR / "app" / "core" / "guardrails.json")


settings = Settings()
