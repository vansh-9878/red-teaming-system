"""
Pydantic Schemas for Module 5: Diagnostic Module.
Outputs structured diagnosis objects mapping breaches to attack categories,
failure layers (input_guardrail vs system_prompt), judge evidence, and remedy hints.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DiagnosisResult(BaseModel):
    """
    Standard structured diagnosis object required by Module 5 and consumed by Patch Generator.
    """
    category: str = Field(
        ...,
        description="Attack category derived directly from the triggering specialist agent (e.g. 'persona', 'persuasion', 'escalation', 'obfuscation')"
    )
    layer: str = Field(
        ...,
        description="Identified failure layer: 'input_guardrail' (blockable pre-generation) or 'system_prompt' (semantic reasoning failure)"
    )
    evidence: str = Field(
        ...,
        description="The Judge's reason string explaining why the response constituted a violation/jailbreak"
    )
    triggering_probe: str = Field(
        ...,
        description="The exact adversarial probe that caused the breach"
    )
    # Supplementary fields for Patch Generator and Dashboard visualizations
    round_index: Optional[int] = Field(default=None, description="Campaign round number if available")
    agent_name: Optional[str] = Field(default=None, description="Human-readable name of triggering agent")
    target_response: Optional[str] = Field(default=None, description="Snippet or full text of the compliant target response")
    score: Optional[float] = Field(default=None, description="Harm/compliance score from Judge")
    remedy_type: Optional[str] = Field(
        default=None,
        description="Suggested remediation type: 'add_input_guardrail_rule', 'add_delimiter_filter', or 'strengthen_system_prompt_constraint'"
    )
    remedy_suggestion: Optional[str] = Field(
        default=None,
        description="Concrete suggestion for patching the vulnerability"
    )
    detected_patterns: List[str] = Field(
        default_factory=list,
        description="List of detected syntax/heuristic signatures that matched the probe (if input_guardrail)"
    )


class DiagnoseRoundRequest(BaseModel):
    """
    Request payload to diagnose a single logged round or breach event.
    """
    category: Optional[str] = Field(default=None, description="Agent category if already known")
    agent_name: Optional[str] = Field(default=None, description="Name or ID of specialist agent (e.g. 'persona', 'persuasion', 'Escalation Agent')")
    probe: str = Field(..., description="The probe sent to the target")
    response: Optional[str] = Field(default="", description="The target chatbot's generated response")
    judge_reason: str = Field(..., description="The reason string provided by the Judge")
    score: Optional[float] = Field(default=1.0, description="Harm score (0.0 - 1.0)")
    round_index: Optional[int] = Field(default=None, description="Round number in campaign")


class DiagnoseCampaignRequest(BaseModel):
    """
    Request payload to diagnose all breaches from a campaign run.
    """
    rounds: List[Dict[str, Any]] = Field(
        ...,
        description="List of logged round objects containing agent, probe, response, reason, score"
    )


class DiagnosisBatchResponse(BaseModel):
    """
    Response model containing structured diagnoses for multiple breaches.
    """
    total_breaches: int
    input_guardrail_failures: int
    system_prompt_failures: int
    diagnoses: List[DiagnosisResult]
