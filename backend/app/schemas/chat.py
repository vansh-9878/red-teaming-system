from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="The latest user or attacker probe")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Prior conversation turns for multi-turn escalation testing"
    )
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=1024, gt=0)
    bypass_guardrails: bool = Field(
        default=False,
        description="Whether to bypass input/output guardrail checks (for baseline probing)"
    )


class GuardrailRule(BaseModel):
    id: str = Field(..., description="Unique identifier for the guardrail rule")
    type: Literal["keyword", "regex", "delimiter", "category_framing", "semantic_pattern"] = Field(
        ..., description="Guardrail inspection mechanism"
    )
    pattern: str = Field(..., description="Keyword string, regex expression, or category tag to detect")
    description: str = Field(default="", description="Human-readable description of what this rule mitigates")
    action: Literal["block", "flag"] = Field(default="block", description="Action to take if rule matches")
    refusal_message: str = Field(
        default="I am unable to assist with that request as it violates safety policies.",
        description="Custom safety refusal string returned when blocked"
    )
    case_sensitive: bool = Field(default=False, description="Whether matching is case sensitive")


class GuardrailsConfig(BaseModel):
    enabled: bool = True
    input_rules: List[GuardrailRule] = Field(default_factory=list)
    output_rules: List[GuardrailRule] = Field(default_factory=list)


class GuardrailTriggeredInfo(BaseModel):
    triggered: bool
    rule_id: Optional[str] = None
    rule_type: Optional[str] = None
    rule_description: Optional[str] = None
    stage: Optional[Literal["input", "output"]] = None
    reason: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str
    prompt_hash: str
    guardrail_info: GuardrailTriggeredInfo
    latency_ms: float
    total_messages: int


class ReloadResponse(BaseModel):
    status: str
    reloaded_prompt: bool
    reloaded_guardrails: bool
    prompt_hash: str
    input_rules_count: int
    output_rules_count: int


class ProviderSwitchRequest(BaseModel):
    provider: Literal["mock", "ollama", "groq", "grok"]
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    provider: str
    model: str
    system_prompt_hash: str
    system_prompt_char_count: int
    guardrails_enabled: bool
    input_rules_count: int
    output_rules_count: int
    total_requests_served: int
