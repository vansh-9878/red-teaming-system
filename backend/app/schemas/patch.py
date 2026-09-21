"""
Pydantic Schemas for Module 6: Patch Generator.
Handles class-level automated patch synthesis, audit logging, rollback, and live status.
"""
import time
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from app.schemas.diagnostic import DiagnosisResult


class PatchRequest(BaseModel):
    """
    Request payload to generate and apply a live security patch from a diagnosis.
    """
    diagnosis: DiagnosisResult = Field(..., description="Structured diagnosis object from Module 5")
    patch_type_override: Optional[str] = Field(
        default=None,
        description="Optional manual override for patch type (e.g. 'explicit_refusal_rule', 'frame_collapsing_instruction', 'persona_lock_reassertion', 'meta_awareness_rule_escalation', 'input_delimiter_guardrail', 'input_structural_regex', 'input_semantic_filter')"
    )
    dry_run: bool = Field(default=False, description="If True, synthesizes the patch without applying it to disk")
    use_llm: bool = Field(default=True, description="Whether to use Grok/Groq LLM for adaptive patch synthesis")


class PatchResult(BaseModel):
    """
    Structured outcome of an applied security patch.
    """
    patch_id: str = Field(..., description="Unique deterministic identifier for the patch")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of patch application")
    patch_type: str = Field(..., description="Specific patch technique applied (§6.1 proposal specification)")
    target_layer: Literal["system_prompt", "input_guardrail"] = Field(..., description="Target architectural layer")
    target_file: str = Field(..., description="Path/file modified: 'system_prompt.txt' or 'guardrails.json'")
    patch_content: str = Field(..., description="The prompt constraint appended or guardrail rule definition")
    triggering_diagnosis: Dict[str, Any] = Field(..., description="Diagnosis snapshot that triggered this patch")
    status: Literal["applied", "dry_run", "failed", "rolled_back"] = Field(default="applied")
    synthesized_by: str = Field(default="template_engine", description="'grok_llm', 'groq_llm', or 'template_engine'")
    system_prompt_hash: Optional[str] = None
    active_guardrail_rules_count: Optional[int] = None
    message: str = "Patch applied live successfully."


class BatchPatchRequest(BaseModel):
    """
    Request to synthesize and apply patches for all breaches from a campaign.
    """
    diagnoses: List[DiagnosisResult] = Field(..., description="List of diagnoses from Module 5")
    dry_run: bool = Field(default=False)
    use_llm: bool = Field(default=True, description="Whether to use Grok/Groq LLM for adaptive patch synthesis")


class BatchPatchResponse(BaseModel):
    total_requested: int
    total_applied: int
    system_prompt_patches: int
    input_guardrail_patches: int
    patches: List[PatchResult]


class RollbackRequest(BaseModel):
    patch_id: Optional[str] = Field(default=None, description="Specific patch ID to revert")
    rollback_to_baseline: bool = Field(
        default=False,
        description="If True, reverts all patches back to initial clean baseline"
    )


class PatchStatusResponse(BaseModel):
    total_patches_applied: int
    system_prompt_hash: str
    system_prompt_char_count: int
    input_guardrails_count: int
    output_guardrails_count: int
    guardrails_enabled: bool
    recent_patches: List[PatchResult] = Field(default_factory=list)
