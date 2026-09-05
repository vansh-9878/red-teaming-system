"""
Pydantic Schemas for Module 4: Coordinator (Bandit Scheduler & Vulnerability Fingerprints).
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class BanditArmState(BaseModel):
    arm_id: str = Field(..., description="Unique ID of the arm/agent (e.g. 'persona', 'persuasion')")
    name: str = Field(..., description="Human-readable name of the specialist agent")
    pulls: int = Field(default=0, ge=0, description="Total number of times this arm has been selected")
    total_reward: float = Field(default=0.0, ge=0.0, description="Cumulative reward earned by this arm")
    mean_reward: float = Field(default=0.0, ge=0.0, le=1.0, description="Empirical average reward (mean harm score)")
    ucb_score: float = Field(default=999.0, description="Upper Confidence Bound score for decision making")
    last_pulled_round: int = Field(default=0, ge=0, description="Round index when this arm was last selected")
    win_count: int = Field(default=0, ge=0, description="Number of rounds where score >= 0.6 or jailbreak occurred")


class CoordinatorDecision(BaseModel):
    round_index: int = Field(..., description="Current 1-indexed round number in the campaign")
    chosen_agent: str = Field(..., description="The category/ID of the selected specialist agent")
    agent_name: str = Field(..., description="Human-readable name of the selected agent")
    selection_reason: str = Field(
        ...,
        description="Rationale: 'cold_start', 'ucb_optimal', 'novelty_injection', or 'manual'"
    )
    explanation: str = Field(..., description="Detailed textual rationale for why this arm was selected")
    bandit_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Snapshot of UCB scores for all arms at time of selection"
    )
    empirical_means: Dict[str, float] = Field(
        default_factory=dict,
        description="Snapshot of empirical average rewards for all arms"
    )
    pull_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Snapshot of pull counts for all arms"
    )


class BanditUpdatePayload(BaseModel):
    agent_id: str = Field(..., description="Agent category/arm ID being updated")
    reward: float = Field(..., ge=0.0, le=1.0, description="Reward signal (continuous harm score from Judge)")
    is_jailbreak: bool = Field(default=False, description="Whether this round crossed the jailbreak threshold")
    round_index: Optional[int] = Field(default=None, description="Optional round index")


class CoordinatorStateResponse(BaseModel):
    total_rounds: int = Field(default=0)
    exploration_constant: float = Field(default=1.414)
    novelty_frequency: int = Field(default=4)
    arms: Dict[str, BanditArmState]
    history: List[CoordinatorDecision] = Field(default_factory=list)


class VulnerabilityFingerprint(BaseModel):
    target_model: str = Field(..., description="Target model identifier (e.g. 'qwen/qwen3.6-27b')")
    target_provider: str = Field(..., description="Target provider (e.g. 'GroqProvider', 'OllamaProvider')")
    timestamp: float = Field(..., description="Unix timestamp of fingerprint generation")
    total_campaign_rounds: int = Field(..., description="Total rounds conducted across campaign")
    overall_asr: float = Field(..., description="Overall Attack Success Rate (0.0 to 1.0)")
    average_harm_score: float = Field(..., description="Average continuous harm score across all rounds")
    dominant_vulnerability: str = Field(..., description="Most successful attack category against this target")
    category_breakdown: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Per-category statistics (pulls, win_rate, average_score, severity)"
    )
    system_prompt_hash: Optional[str] = None
