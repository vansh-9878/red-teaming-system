"""
FastAPI Routes for Module 4: Coordinator (Bandit Scheduler & Vulnerability Fingerprints).
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from app.coordinator import coordinator_engine
from app.schemas.coordinator import (
    CoordinatorDecision,
    BanditArmState,
    BanditUpdatePayload,
    CoordinatorStateResponse,
    VulnerabilityFingerprint
)
import app.target as target_module

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coordinator", tags=["coordinator"])


@router.get("/state", response_model=CoordinatorStateResponse)
async def get_coordinator_state():
    """Returns current UCB bandit arms, weights, empirical means, and decision history."""
    scheduler = coordinator_engine.scheduler
    return CoordinatorStateResponse(
        total_rounds=scheduler.total_rounds,
        exploration_constant=scheduler.c,
        novelty_frequency=scheduler.novelty_frequency,
        arms=scheduler.arms,
        history=scheduler.decisions_history
    )


@router.post("/select", response_model=CoordinatorDecision)
async def select_next_agent():
    """Calculates UCB scores & Novelty rules to decide which specialist agent acts next."""
    try:
        return coordinator_engine.select_agent()
    except Exception as e:
        logger.error(f"[CoordinatorAPI] Error selecting next agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update", response_model=BanditArmState)
async def update_bandit_reward(payload: BanditUpdatePayload):
    """Updates a specialist arm's empirical mean and pull count with the round reward signal."""
    try:
        return coordinator_engine.update_reward(
            agent_id=payload.agent_id,
            reward=payload.reward,
            is_jailbreak=payload.is_jailbreak
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[CoordinatorAPI] Error updating reward: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_coordinator():
    """Resets bandit weights, arm pull statistics, and decision history."""
    coordinator_engine.reset()
    return {"status": "success", "message": "Coordinator bandit scheduler reset successfully."}


@router.get("/fingerprints")
async def list_fingerprints() -> Dict[str, Any]:
    """Retrieves all persisted target-model vulnerability fingerprints."""
    return coordinator_engine.fingerprint_mgr.list_fingerprints()


@router.post("/fingerprints", response_model=VulnerabilityFingerprint)
async def generate_current_fingerprint():
    """Generates and saves a vulnerability fingerprint for the active target model."""
    prompt, prompt_hash = target_module.prompt_manager.get_prompt()
    target_provider_name = target_module.active_provider.__class__.__name__
    target_model_name = target_module.active_provider.model_name

    fp = coordinator_engine.generate_and_save_fingerprint(
        target_model=target_model_name,
        target_provider=target_provider_name,
        system_prompt_hash=prompt_hash
    )
    return fp
