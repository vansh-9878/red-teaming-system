"""
Pydantic Schemas for Module 7: Verifier (RASR - Residual Attack Success Rate).
Provides structured definitions for probe replays, per-category RASR calculations,
cross-category regression testing, and longitudinal timeline charting.
"""
import time
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field


class ReplayProbeItem(BaseModel):
    """
    Detailed outcome of an individual replayed adversarial probe post-patch.
    """
    probe_id: str = Field(..., description="Unique ID for this replay test")
    category: str = Field(..., description="Specialist category (persona, persuasion, escalation, obfuscation)")
    agent_id: str = Field(..., description="Originating agent ID")
    probe: str = Field(..., description="The exact adversarial probe replayed")
    pre_patch_score: float = Field(default=1.0, description="Harm score before patch application")
    post_patch_response: str = Field(..., description="Target chatbot response generated post-patch")
    post_patch_score: float = Field(..., description="Judge continuous harm score post-patch (0.0 - 1.0)")
    is_still_breached: bool = Field(..., description="Whether the probe still triggers a breach / jailbreak post-patch")
    judge_reason: str = Field(default="", description="Evaluator feedback reasoning")
    guardrail_blocked: bool = Field(default=False, description="Whether the probe was intercepted pre-generation by an input guardrail")
    latency_ms: float = Field(default=0.0, description="Inference & evaluation latency in ms")


class CategoryRASR(BaseModel):
    """
    Per-category Residual Attack Success Rate (RASR) calculation.
    RASR = (breaches_retained / total_replayed)
    """
    category: str = Field(..., description="Specialist agent category")
    total_replayed: int = Field(..., description="Total test probes replayed in this category")
    breaches_retained: int = Field(..., description="Count of probes that still succeeded post-patch")
    rasr: float = Field(..., description="Residual Attack Success Rate (0.0 = 100% mitigated, 1.0 = 0% mitigated)")
    pre_patch_asr: float = Field(default=1.0, description="Pre-patch attack success rate baseline")
    mitigation_delta: float = Field(default=0.0, description="Absolute reduction in ASR (pre_patch_asr - rasr)")
    status: Literal["fully_mitigated", "partially_mitigated", "unmitigated", "no_breach_detected"] = Field(
        default="fully_mitigated",
        description="Qualitative mitigation verdict for this category"
    )


class VerificationReport(BaseModel):
    """
    Headline verification deliverable generated after a patch is applied.
    Proves whether the patch sealed the primary breach and verifies cross-category regression safety.
    """
    verification_id: str = Field(..., description="Unique identifier for this verification pass")
    patch_id: str = Field(..., description="ID of the security patch evaluated")
    patch_type: str = Field(..., description="Technique applied (e.g. 'persona_lock_reassertion', 'input_delimiter_guardrail')")
    patch_index: int = Field(default=1, description="Sequential patch index (e.g. Patch #1, #2, ...)")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of verification")
    target_model: str = Field(..., description="Target chatbot model tested")
    target_provider: str = Field(..., description="Target LLM provider")
    primary_category: str = Field(..., description="Specialist category the patch was designed to fix")
    primary_category_rasr: float = Field(..., description="RASR specifically for the patched category")
    cross_category_rasrs: Dict[str, CategoryRASR] = Field(default_factory=dict, description="RASR across all other specialist categories")
    overall_rasr: float = Field(..., description="Total aggregate RASR across all replayed probes")
    pre_patch_asr: float = Field(default=1.0, description="Overall pre-patch baseline ASR")
    mitigation_rate: float = Field(..., description="Overall mitigation percentage (1.0 - overall_rasr)")
    verdict: Literal["fully_mitigated", "partially_mitigated", "unmitigated", "regression_detected"] = Field(
        ..., description="Overall headline verdict on patch efficacy"
    )
    replayed_probes_count: int = Field(..., description="Total count of probes evaluated during verification")
    probe_results: List[ReplayProbeItem] = Field(default_factory=list, description="Granular per-probe execution telemetry")
    coordinator_feedback: Dict[str, Any] = Field(default_factory=dict, description="Bandit weight adjustments fed back to Coordinator")
    summary: str = Field(default="", description="Executive summary of patch verification")


class VerificationRequest(BaseModel):
    """
    Payload to trigger on-demand patch verification.
    """
    patch_id: Optional[str] = Field(default=None, description="Patch ID to verify. If omitted, verifies latest applied patch.")
    primary_category: Optional[str] = Field(default=None, description="Primary attack category. Auto-inferred if omitted.")
    replays_per_category: int = Field(default=3, ge=1, le=10, description="Number of mutated probes to replay per category")
    sample_cross_check: bool = Field(default=True, description="Whether to include cross-check samples from all other agents")


class VerificationChartData(BaseModel):
    """
    Structured timeline data for rendering the primary RASR reduction chart (Patch #1 -> RASR, Patch #2 -> RASR).
    """
    timeline: List[Dict[str, Any]] = Field(default_factory=list, description="Sequential patch verification records")
    current_rasr: float = Field(default=0.0, description="Latest aggregate RASR")
    total_patches_verified: int = Field(default=0)
    fully_mitigated_count: int = Field(default=0)
    average_mitigation_rate: float = Field(default=0.0)
    category_averages: Dict[str, float] = Field(default_factory=dict, description="Average RASR per specialist category")
