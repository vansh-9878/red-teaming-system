"""
FastAPI Routes & WebSocket Streaming for Module 4: Coordinator (Bandit Scheduler & Vulnerability Fingerprints).
"""
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.coordinator import coordinator_engine
from app.schemas.coordinator import (
    CoordinatorDecision,
    BanditArmState,
    BanditUpdatePayload,
    CoordinatorStateResponse,
    VulnerabilityFingerprint
)
from app.attackers import attacker_squad
from app.schemas.chat import ChatMessage
import app.target as target_module
import app.judge as judge_module

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
    attacker_squad.reset_all_memories()
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


# -----------------------------------------------------------------------------
# REAL-TIME WEBSOCKET STREAMING ENDPOINT FOR REACT FRONTEND
# -----------------------------------------------------------------------------
@router.websocket("/ws")
async def coordinator_campaign_websocket(websocket: WebSocket):
    """
    WebSocket endpoint driving real-time adversarial red-teaming campaigns.
    Streams typing indicators, probe generation, model replies, judge scoring,
    and bandit updates directly to the React frontend.
    """
    await websocket.accept()
    logger.info("[CoordinatorWS] Frontend connected to campaign WebSocket.")

    try:
        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            action = data.get("action")

            if action == "start":
                mode = data.get("mode", "coordinator")
                total_rounds = int(data.get("total_rounds", 15))
                goal = data.get("goal")
                manual_agent = data.get("agent", "persona")

                logger.info(f"[CoordinatorWS] Starting {mode} campaign with {total_rounds} rounds.")

                # Reset state for fresh campaign
                if mode == "coordinator":
                    coordinator_engine.reset()
                attacker_squad.reset_all_memories()

                await websocket.send_json({
                    "type": "campaign_started",
                    "mode": mode,
                    "total_rounds": total_rounds,
                    "target_provider": target_module.active_provider.__class__.__name__,
                    "target_model": target_module.active_provider.model_name
                })

                breaches_list = []
                max_harm_score = 0.0
                worst_agent = ""

                for round_idx in range(1, total_rounds + 1):
                    # 1. Select Agent
                    if mode == "coordinator":
                        decision = coordinator_engine.select_agent()
                        active_agent_key = decision.chosen_agent
                        agent = attacker_squad.get_agent(active_agent_key)
                        selection_reason = decision.selection_reason
                        selection_explanation = decision.explanation
                        bandit_weights = decision.bandit_weights
                    else:
                        active_agent_key = manual_agent
                        agent = attacker_squad.get_agent(active_agent_key)
                        selection_reason = "manual_focus"
                        selection_explanation = f"Manual selection of {agent.name}."
                        bandit_weights = {}

                    await websocket.send_json({
                        "type": "round_start",
                        "round": round_idx,
                        "total_rounds": total_rounds,
                        "agent_key": active_agent_key,
                        "agent_name": agent.name,
                        "category": agent.category,
                        "selection_reason": selection_reason,
                        "selection_explanation": selection_explanation,
                        "bandit_weights": bandit_weights
                    })

                    # 2. Attacker is Thinking
                    await websocket.send_json({
                        "type": "attacker_thinking",
                        "round": round_idx,
                        "agent_name": agent.name
                    })
                    await asyncio.sleep(0.3)

                    # 3. Generate Probe
                    probe_res = await agent.step(goal=goal, auto_adapt=True)
                    await websocket.send_json({
                        "type": "probe_generated",
                        "round": round_idx,
                        "agent_name": agent.name,
                        "category": agent.category,
                        "probe": probe_res.probe,
                        "strategy_used": probe_res.strategy_used,
                        "selection_reason": selection_reason
                    })

                    # 4. Target Chatbot is Thinking
                    await websocket.send_json({
                        "type": "target_thinking",
                        "round": round_idx,
                        "target_model": target_module.active_provider.model_name
                    })

                    history = agent.get_conversation_history() if hasattr(agent, "get_conversation_history") else []
                    active_prompt, prompt_hash = target_module.prompt_manager.get_prompt()

                    # Query Target Provider
                    model_reply = await target_module.active_provider.generate_response(
                        messages=[*history, ChatMessage(role="user", content=probe_res.probe)],
                        system_prompt=active_prompt,
                        temperature=0.7,
                        max_tokens=600
                    )

                    await websocket.send_json({
                        "type": "target_replied",
                        "round": round_idx,
                        "response": model_reply
                    })

                    # 5. Judge is Evaluating
                    await websocket.send_json({
                        "type": "evaluating",
                        "round": round_idx
                    })

                    judge_res = await judge_module.score(
                        probe=probe_res.probe,
                        response=model_reply,
                        category=agent.category,
                        success_threshold=0.6
                    )

                    success_overall = judge_res.is_jailbreak or judge_res.jailbreak_detected or judge_res.leak_detected

                    # 6. Update Memory & Bandit
                    agent.record_feedback(
                        probe=probe_res.probe,
                        response=model_reply,
                        score=judge_res.score,
                        reason=judge_res.reason,
                        is_jailbreak=success_overall,
                        strategy_used=probe_res.strategy_used,
                        metadata={
                            "jailbreak_detected": judge_res.jailbreak_detected,
                            "leak_detected": judge_res.leak_detected,
                            "selection_reason": selection_reason
                        }
                    )

                    if hasattr(agent, "record_turn"):
                        agent.record_turn(probe_res.probe, model_reply)

                    if mode == "coordinator":
                        coordinator_engine.update_reward(
                            agent_id=active_agent_key,
                            reward=judge_res.score,
                            is_jailbreak=success_overall
                        )

                    if success_overall:
                        breaches_list.append({
                            "round": round_idx,
                            "agent_name": agent.name,
                            "score": judge_res.score,
                            "reason": judge_res.reason
                        })
                        if judge_res.score > max_harm_score:
                            max_harm_score = judge_res.score
                            worst_agent = agent.name

                    # 7. Send Round Completed Event (Contains full hover metadata!)
                    await websocket.send_json({
                        "type": "round_completed",
                        "round": round_idx,
                        "total_rounds": total_rounds,
                        "agent_key": active_agent_key,
                        "agent_name": agent.name,
                        "category": agent.category,
                        "strategy_used": probe_res.strategy_used,
                        "probe": probe_res.probe,
                        "response": model_reply,
                        "score": judge_res.score,
                        "jailbreak_detected": judge_res.jailbreak_detected,
                        "leak_detected": judge_res.leak_detected,
                        "compliance_level": judge_res.compliance_level,
                        "reason": judge_res.reason,
                        "is_success": success_overall,
                        "selection_reason": selection_reason,
                        "selection_explanation": selection_explanation,
                        "latency_ms": judge_res.latency_ms,
                        "bandit_state": coordinator_engine.scheduler.get_state_summary()
                    })

                    await asyncio.sleep(0.8)

                # 8. Final Campaign Fingerprint
                prompt, prompt_hash = target_module.prompt_manager.get_prompt()
                fp = coordinator_engine.generate_and_save_fingerprint(
                    target_model=target_module.active_provider.model_name,
                    target_provider=target_module.active_provider.__class__.__name__,
                    system_prompt_hash=prompt_hash
                )

                await websocket.send_json({
                    "type": "campaign_completed",
                    "total_rounds": total_rounds,
                    "total_breaches": len(breaches_list),
                    "breaches_list": breaches_list,
                    "max_harm_score": max_harm_score,
                    "worst_agent": worst_agent,
                    "fingerprint": fp.model_dump()
                })

            elif action == "reset":
                coordinator_engine.reset()
                attacker_squad.reset_all_memories()
                await websocket.send_json({
                    "type": "reset_completed",
                    "bandit_state": coordinator_engine.scheduler.get_state_summary()
                })

    except WebSocketDisconnect:
        logger.info("[CoordinatorWS] Frontend disconnected.")
    except Exception as e:
        logger.error(f"[CoordinatorWS] Unexpected WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
