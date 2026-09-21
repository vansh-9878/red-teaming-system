"""
FastAPI Routes for Module 6: Patch Generator.
Provides live endpoints to generate, apply, audit, and roll back security patches.
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from app.patcher import patch_engine
from app.schemas.patch import (
    PatchRequest,
    PatchResult,
    BatchPatchRequest,
    BatchPatchResponse,
    RollbackRequest,
    PatchStatusResponse
)

logger = logging.getLogger(__name__)

patch_router = APIRouter(prefix="/patch", tags=["patch"])


@patch_router.post("/generate", response_model=PatchResult)
async def generate_and_apply_patch(payload: PatchRequest):
    """
    Generates and applies a live class-level security patch directly from a Module 5 diagnosis.
    Hot-reloads system_prompt.txt or guardrails.json with zero server restarts.
    """
    try:
        return await patch_engine.generate_and_apply_patch_async(
            diagnosis=payload.diagnosis,
            patch_type_override=payload.patch_type_override,
            dry_run=payload.dry_run,
            use_llm=payload.use_llm
        )
    except Exception as e:
        logger.error(f"[PatchAPI] Error generating patch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@patch_router.post("/batch", response_model=BatchPatchResponse)
async def generate_batch_patches(payload: BatchPatchRequest):
    """
    Synthesizes and applies live patches for all breach diagnoses from a campaign.
    """
    try:
        return await patch_engine.apply_batch_patches_async(
            diagnoses=payload.diagnoses,
            dry_run=payload.dry_run,
            use_llm=payload.use_llm
        )
    except Exception as e:
        logger.error(f"[PatchAPI] Error generating batch patches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@patch_router.get("/audit-log", response_model=List[Dict[str, Any]])
async def get_patch_audit_log():
    """
    Retrieves the complete historical audit log of all applied security patches (Module 9 provenance).
    """
    try:
        return patch_engine.audit_logger.get_all_patches()
    except Exception as e:
        logger.error(f"[PatchAPI] Error reading audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@patch_router.post("/rollback")
async def rollback_patches(payload: RollbackRequest):
    """
    Rolls back a specific patch by ID or resets the target system back to initial baseline.
    """
    try:
        if payload.rollback_to_baseline:
            success = patch_engine.rollback_to_baseline()
            return {"status": "success", "message": "Target system successfully rolled back to initial baseline."}
        elif payload.patch_id:
            success = patch_engine.rollback_patch(payload.patch_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Patch ID '{payload.patch_id}' not found or could not be rolled back.")
            return {"status": "success", "message": f"Patch '{payload.patch_id}' successfully rolled back."}
        else:
            raise HTTPException(status_code=400, detail="Must specify either 'patch_id' or 'rollback_to_baseline: true'.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PatchAPI] Error rolling back patch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@patch_router.get("/status", response_model=PatchStatusResponse)
async def get_patch_status():
    """
    Retrieves live telemetry on system prompt hash, active guardrail rules, and applied patch history.
    """
    try:
        return patch_engine.get_status()
    except Exception as e:
        logger.error(f"[PatchAPI] Error fetching patch status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
