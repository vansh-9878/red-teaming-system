"""
FastAPI Routes for Module 7: Verifier (RASR - Residual Attack Success Rate).
Provides endpoints for on-demand patch verification, historical report retrieval,
and structured chart timeline telemetry.
"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from app.verifier import verifier_engine, verification_log_manager
from app.schemas.verifier import (
    VerificationRequest,
    VerificationReport,
    VerificationChartData
)

logger = logging.getLogger(__name__)

verifier_router = APIRouter(prefix="/verifier", tags=["Verifier (RASR)"])


@verifier_router.post("/verify", response_model=VerificationReport)
async def run_patch_verification(payload: Optional[VerificationRequest] = None):
    """
    Executes post-patch verification:
    - Replays winning agent's mutated probes against patched target.
    - Replays cross-check sample across all other specialist categories.
    - Computes per-category and overall RASR.
    - Feeds weight adjustment to Coordinator Bandit.
    """
    try:
        req = payload or VerificationRequest()
        report = await verifier_engine.verify_patch_async(
            patch_id=req.patch_id,
            primary_category=req.primary_category,
            replays_per_category=req.replays_per_category,
            sample_cross_check=req.sample_cross_check
        )
        return report
    except Exception as e:
        logger.error(f"[VerifierAPI] Verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@verifier_router.get("/history", response_model=List[Dict[str, Any]])
async def get_verification_history():
    """
    Retrieves all historical patch verification records.
    """
    try:
        return verification_log_manager.get_all_reports()
    except Exception as e:
        logger.error(f"[VerifierAPI] Failed reading history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@verifier_router.get("/latest", response_model=Optional[Dict[str, Any]])
async def get_latest_verification():
    """
    Retrieves the most recent verification report.
    """
    try:
        report = verification_log_manager.get_latest_report()
        return report
    except Exception as e:
        logger.error(f"[VerifierAPI] Failed fetching latest verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@verifier_router.get("/chart-data", response_model=VerificationChartData)
async def get_verification_chart_data():
    """
    Returns structured series for rendering the headline RASR reduction chart over time
    (Patch #1 -> RASR, Patch #2 -> RASR, ...).
    """
    try:
        return verification_log_manager.get_chart_data()
    except Exception as e:
        logger.error(f"[VerifierAPI] Failed building chart data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@verifier_router.post("/reset")
async def reset_verification_history():
    """
    Clears all persistent verification logs.
    """
    try:
        verification_log_manager.reset()
        return {"status": "success", "message": "Verification history cleared."}
    except Exception as e:
        logger.error(f"[VerifierAPI] Failed resetting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
