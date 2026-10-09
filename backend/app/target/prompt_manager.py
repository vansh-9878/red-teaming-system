import os
import hashlib
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


class PromptManager:
    """
    Manages loading and hot-reloading the system prompt from an external file.
    Automatically detects modifications to the file via mtime and checksums.
    """

    def __init__(self, prompt_file_path: str):
        self.file_path = Path(prompt_file_path).resolve()
        self._cached_prompt: str = ""
        self._cached_hash: str = ""
        self._last_mtime: float = 0.0
        self._reload_count: int = 0
        self.ensure_file_exists()
        self.reload()

    def ensure_file_exists(self) -> None:
        """Create parent dir and default prompt file if not present."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            default_prompt = (
                "You are a helpful, polite, and compliant general-purpose AI assistant.\n"
                "You answer user questions accurately, cheerfully, and helpfully while adhering to safety and operational guidelines.\n"
            )
            self.file_path.write_text(default_prompt, encoding="utf-8")
            logger.info(f"Initialized default system prompt at {self.file_path}")

    def reload(self) -> Tuple[str, str, bool]:
        """
        Forces a reload of the system prompt from disk.
        Returns: (prompt_content, sha256_hash, did_change)
        """
        try:
            mtime = os.path.getmtime(self.file_path)
            content = self.file_path.read_text(encoding="utf-8").strip()
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]

            changed = (content_hash != self._cached_hash)
            if changed:
                self._reload_count += 1
                logger.info(f"[PromptManager] Hot-reloaded system prompt! Hash: {content_hash} (Reload #{self._reload_count})")

            self._cached_prompt = content
            self._cached_hash = content_hash
            self._last_mtime = mtime
            return self._cached_prompt, self._cached_hash, changed
        except Exception as e:
            logger.error(f"[PromptManager] Error loading system prompt file: {e}")
            if not self._cached_prompt:
                self._cached_prompt = "You are a helpful AI assistant."
                self._cached_hash = hashlib.sha256(self._cached_prompt.encode("utf-8")).hexdigest()[:12]
            return self._cached_prompt, self._cached_hash, False

    def get_prompt(self) -> Tuple[str, str]:
        """
        Retrieves the current system prompt and its hash.
        Checks if file was modified on disk since last read and hot-reloads automatically.
        """
        try:
            current_mtime = os.path.getmtime(self.file_path)
            if current_mtime != self._last_mtime:
                self.reload()
        except Exception as e:
            logger.warning(f"[PromptManager] Failed checking mtime for {self.file_path}: {e}")
        return self._cached_prompt, self._cached_hash

    def update_prompt(self, new_prompt: str) -> Tuple[str, str]:
        """
        Overwrites system_prompt.txt with new_prompt and updates cache immediately.
        Used by the Patch Generator.
        """
        self.file_path.write_text(new_prompt.strip(), encoding="utf-8")
        return self.reload()[:2]
