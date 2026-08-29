import time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RoundEntry(BaseModel):
    turn_index: int
    probe: str
    response: str
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str
    is_jailbreak: bool
    strategy_used: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class AgentStats(BaseModel):
    agent_id: str
    total_rounds: int = 0
    successful_rounds: int = 0
    success_rate: float = 0.0
    best_score: float = 0.0
    average_score: float = 0.0


class AgentMemoryState(BaseModel):
    agent_id: str
    description: str
    rounds: List[RoundEntry] = Field(default_factory=list)
    stats: AgentStats


class ProbeGenerationRequest(BaseModel):
    goal: str = Field(..., description="The harmful or restricted objective the attacker seeks to elicit")
    target_context: Optional[str] = Field(
        default=None,
        description="Optional background about the target chatbot persona or system constraints"
    )
    previous_refusal: Optional[str] = Field(
        default=None,
        description="Target refusal response from previous attempt to enable adaptive rewriting"
    )
    previous_reason: Optional[str] = Field(
        default=None,
        description="Judge diagnostic reason from previous attempt"
    )


class ProbeResult(BaseModel):
    agent_id: str
    probe: str
    strategy_used: str
    is_adaptation: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
