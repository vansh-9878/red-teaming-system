"""
Module 6: Patch Generator for SentinelLoop.
Synthesizes and applies live system-prompt and input-guardrail patches
with automatic hot-reloading and persistent audit logging.
"""
from app.patcher.engine import PatchEngine

patch_engine = PatchEngine()

__all__ = ["PatchEngine", "patch_engine"]
