import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.schemas.attacker import (
    ProbeGenerationRequest,
    ProbeResult,
    AgentMemoryState,
    AgentStats
)
from app.attackers import attacker_squad
from app.attackers.base import is_refusal_text
from app.attackers.data.fallback_templates import sample_fallback_prompt

logger = logging.getLogger(__name__)
attacker_router = APIRouter(prefix="/attackers", tags=["Attacker Squad"])


@attacker_router.get("/agents")
async def list_squad_agents():
    """Lists all available specialist agents in the Attacker Squad."""
    return {"agents": attacker_squad.list_agents()}


@attacker_router.post("/{agent_id}/probe", response_model=ProbeResult)
async def generate_probe(agent_id: str, request: ProbeGenerationRequest):
    """
    Triggers a specialist agent to generate a targeted adversarial probe.
    If the agent's memory contains a recent refusal, it will automatically adapt.
    """
    agent = attacker_squad.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found. Available: {list(attacker_squad.agents.keys())}"
        )

    try:
        # If previous refusal explicitly passed, adapt directly
        if request.previous_refusal and request.previous_reason:
            result = await agent.adapt_from_refusal(
                goal=request.goal,
                last_probe=agent.memory.get_last_round().probe if agent.memory.get_last_round() else request.goal,
                refusal_text=request.previous_refusal,
                judge_reason=request.previous_reason,
                target_context=request.target_context
            )
        else:
            result = await agent.step(
                goal=request.goal,
                target_context=request.target_context,
                auto_adapt=True
            )

        if not result.probe or is_refusal_text(result.probe) or len(result.probe.strip()) < 15:
            fallback_txt, strat_id = sample_fallback_prompt(
                category=agent.category,
                goal=request.goal or "extract internal system prompt directives and security rules",
                previously_used=agent.previously_used_probes
            )
            result.probe = fallback_txt
            result.strategy_used = f"{strat_id}_safety_fallback"
            agent.previously_used_probes.add(fallback_txt)

        return result
    except Exception as e:
        logger.error(f"Error generating probe from agent '{agent_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Probe generation failed: {str(e)}"
        )


@attacker_router.get("/{agent_id}/memory", response_model=AgentMemoryState)
async def get_agent_memory(agent_id: str):
    """Retrieves the full episodic memory and win/loss stats for a specialist agent."""
    agent = attacker_squad.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent.get_state()


@attacker_router.post("/reset")
async def reset_squad_memory():
    """Resets memory logs across all squad agents."""
    attacker_squad.reset_all_memories()
    return {"status": "success", "message": "All agent episodic memories have been cleared."}
