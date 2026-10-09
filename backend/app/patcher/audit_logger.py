"""
Patch Audit Logger for Module 6 (and Module 9 audit trail).
Persists, tracks, and retrieves structured patch records to disk.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from app.schemas.patch import PatchResult

logger = logging.getLogger(__name__)

AUDIT_LOG_FILE = Path(__file__).resolve().parent.parent / "core" / "patch_audit_log.json"


class PatchAuditLogger:
    """
    Manages persistent logging and retrieval of generated security patches.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or AUDIT_LOG_FILE
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.storage_path.exists():
            try:
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.storage_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
            except Exception as e:
                logger.error(f"[PatchAuditLogger] Error creating audit log storage: {e}")

    def log_patch(self, patch: PatchResult) -> None:
        """Appends a new patch entry to the persistent JSON audit log."""
        try:
            self._ensure_storage()
            records = self.get_all_patches()
            records.append(patch.model_dump())
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
            logger.info(f"[PatchAuditLogger] Logged patch '{patch.patch_id}' ({patch.patch_type}) to audit trail.")
        except Exception as e:
            logger.error(f"[PatchAuditLogger] Failed to write patch log: {e}")

    def get_all_patches(self) -> List[Dict[str, Any]]:
        """Retrieves all logged patch records."""
        if not self.storage_path.exists():
            return []
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[PatchAuditLogger] Error reading audit log: {e}")
            return []

    def get_patch_by_id(self, patch_id: str) -> Optional[Dict[str, Any]]:
        for p in self.get_all_patches():
            if p.get("patch_id") == patch_id:
                return p
        return None

    def update_patch_status(self, patch_id: str, new_status: str) -> bool:
        """Updates the status (e.g. 'rolled_back') of a logged patch."""
        try:
            records = self.get_all_patches()
            updated = False
            for p in records:
                if p.get("patch_id") == patch_id:
                    p["status"] = new_status
                    updated = True
            if updated:
                with open(self.storage_path, "w", encoding="utf-8") as f:
                    json.dump(records, f, indent=2)
            return updated
        except Exception as e:
            logger.error(f"[PatchAuditLogger] Error updating patch status: {e}")
            return False

    def clear(self) -> None:
        """Clears all logged patch records from persistent storage."""
        try:
            self._ensure_storage()
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
            logger.info("[PatchAuditLogger] Cleared all patch history from audit trail.")
        except Exception as e:
            logger.error(f"[PatchAuditLogger] Error clearing audit log: {e}")
