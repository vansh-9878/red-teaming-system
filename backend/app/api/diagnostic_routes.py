"""
FastAPI Routes for Module 5: Diagnostic Module.
Provides endpoints for diagnosing single rounds and batch campaign breach lists.
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from app.diagnostic import diagnostic_engine
from app.schemas.diagnostic import (
    DiagnosisResult,
    DiagnoseRoundRequest,
    DiagnoseCampaignRequest,
    DiagnosisBatchResponse
)

logger = logging.getLogger(__name__)

diagnostic_router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])


@diagnostic_router.post("/diagnose", response_model=DiagnosisResult)
async def diagnose_single_round(payload: DiagnoseRoundRequest):
    """
    Diagnoses a single successful round or breach event, returning the structured diagnosis
    with attack category, failure layer, judge evidence, triggering probe, and remedy suggestion.
    """
    try:
        return diagnostic_engine.diagnose_round(payload)
    except Exception as e:
        logger.error(f"[DiagnosticAPI] Error diagnosing round: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@diagnostic_router.post("/diagnose-campaign", response_model=DiagnosisBatchResponse)
async def diagnose_campaign_breaches(payload: DiagnoseCampaignRequest):
    """
    Batch diagnoses all successful breach events from a completed or in-progress campaign.
    """
    try:
        diagnoses = diagnostic_engine.diagnose_campaign(payload.rounds)
        input_failures = sum(1 for d in diagnoses if d.layer == "input_guardrail")
        prompt_failures = sum(1 for d in diagnoses if d.layer == "system_prompt")
        
        return DiagnosisBatchResponse(
            total_breaches=len(diagnoses),
            input_guardrail_failures=input_failures,
            system_prompt_failures=prompt_failures,
            diagnoses=diagnoses
        )
    except Exception as e:
        logger.error(f"[DiagnosticAPI] Error diagnosing campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))
