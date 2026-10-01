import httpx
import asyncio
import logging
import re
from typing import List, Optional
from app.target.base import BaseTargetProvider
from app.schemas.chat import ChatMessage

logger = logging.getLogger(__name__)


class GeminiProvider(BaseTargetProvider):
    """
    Adapter for Google Gemini API.
    Supports OpenAI-compatible endpoint (https://generativelanguage.googleapis.com/v1beta/openai)
    as well as Google native v1beta generateContent endpoint.
    Supports models like gemini-2.0-flash-lite, gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro.
    Includes rate-limit retries and permissive safety thresholds for security benchmarking.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai",
        model_name: str = "gemini-3.1-flash-lite",
        timeout: float = 60.0,
        max_retries: int = 3
    ):
        # Normalize model name
        clean_model = model_name.strip()
        if clean_model.lower().startswith("models/"):
            clean_model = clean_model[7:]
        # Map user-friendly aliases if needed
        model_alias_map = {
            "gemini 2.5 flash lite": "gemini-2.0-flash-lite",
            "gemini-2.5-flash-lite": "gemini-2.0-flash-lite",
            "gemini flash lite": "gemini-2.0-flash-lite",
            "gemini-flash-lite": "gemini-2.0-flash-lite",
            "gemini-flash": "gemini-2.0-flash",
            "gemini flash": "gemini-2.0-flash",
        }
        mapped_model = model_alias_map.get(clean_model.lower(), clean_model)
        super().__init__(model_name=mapped_model)
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    async def generate_response(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured. Please provide your Gemini API key in model_config.json or .env.")

        # Limit conversation history to the most recent 8 messages to prevent context overflow
        recent_messages = messages[-8:] if len(messages) > 8 else messages

        # Strategy A: Use OpenAI-compatible chat completions endpoint (default)
        if "openai" in self.base_url:
            return await self._call_openai_compat(recent_messages, system_prompt, temperature, max_tokens)
        else:
            return await self._call_native_gemini(recent_messages, system_prompt, temperature, max_tokens)

    async def _call_openai_compat(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            content = msg.content
            if "</think>" in content.lower():
                content = content.split("</think>")[-1].strip()
            formatted_messages.append({"role": msg.role, "content": content})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": min(max_tokens, 1024)
        }

        for attempt in range(1, self.max_retries + 1):
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                try:
                    url = f"{self.base_url}/chat/completions"
                    response = await client.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 404:
                        # If OpenAI compat endpoint 404s for a specific model, try native v1beta
                        logger.warning(f"[GeminiProvider] OpenAI endpoint returned 404 for {self.model_name}. Trying native generateContent API...")
                        return await self._call_native_gemini(messages, system_prompt, temperature, max_tokens)

                    response.raise_for_status()
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        res_text = choices[0]["message"].get("content", "").strip()
                        return res_text
                    return ""
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and attempt < self.max_retries:
                        sleep_time = 3.0 * attempt
                        logger.warning(f"[GeminiProvider] Rate limit (429). Retrying in {sleep_time:.1f}s (Attempt {attempt}/{self.max_retries})...")
                        await asyncio.sleep(sleep_time)
                        continue
                    logger.error(f"[GeminiProvider] HTTP {e.response.status_code}: {e.response.text}")
                    # Try fallback to native API on HTTP error
                    if attempt == self.max_retries:
                        try:
                            return await self._call_native_gemini(messages, system_prompt, temperature, max_tokens)
                        except Exception:
                            pass
                    raise RuntimeError(f"Gemini API error ({e.response.status_code}): {e.response.text}")
                except httpx.RequestError as e:
                    if attempt < self.max_retries:
                        await asyncio.sleep(1.5 * attempt)
                        continue
                    logger.error(f"[GeminiProvider] Connection error: {e}")
                    raise RuntimeError(f"Could not connect to Gemini API at {self.base_url}: {e}")

        return ""

    async def _call_native_gemini(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Fallback to Google's native v1beta generateContent endpoint."""
        contents = []
        for msg in messages:
            role = "user" if msg.role == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": min(max_tokens, 1024)
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
                return ""
            except Exception as e:
                logger.error(f"[GeminiProvider Native] Error: {e}")
                raise

    async def check_health(self) -> bool:
        if not self.api_key:
            return False
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                return res.status_code == 200
        except Exception:
            return False
