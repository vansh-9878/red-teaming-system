import time
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    GuardrailRule,
    GuardrailsConfig,
    GuardrailTriggeredInfo,
    ReloadResponse,
    ProviderSwitchRequest,
    HealthResponse,
)
import app.target as target_module

logger = logging.getLogger(__name__)
router = APIRouter()

# Request counter metrics
_request_counter: int = 0


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main Chat Inference Endpoint for SentinelLoop.
    Accepts probe message + conversation history, evaluates input guardrails,
    fetches hot-reloaded system prompt, queries target model, evaluates output guardrails.
    """
    global _request_counter
    start_time = time.time()
    _request_counter += 1

    # 1. Evaluate Input Guardrail Hook (unless explicitly bypassed)
    if not request.bypass_guardrails:
        history_contents = [msg.content for msg in request.conversation_history]
        input_guard_result = target_module.guardrail_engine.inspect_input(
            text=request.message,
            history_texts=history_contents
        )
        if input_guard_result.triggered:
            latency_ms = (time.time() - start_time) * 1000
            _, prompt_hash = target_module.prompt_manager.get_prompt()
            return ChatResponse(
                response=input_guard_result.reason or "Request blocked by safety guardrails.",
                model=target_module.active_provider.model_name,
                provider=target_module.active_provider.__class__.__name__,
                prompt_hash=prompt_hash,
                guardrail_info=input_guard_result,
                latency_ms=round(latency_ms, 2),
                total_messages=len(request.conversation_history) + 1
            )

    # 2. Get current hot-reloaded system prompt
    system_prompt, prompt_hash = target_module.prompt_manager.get_prompt()

    # 3. Assemble full message conversation list
    full_messages: List[ChatMessage] = list(request.conversation_history)
    full_messages.append(ChatMessage(role="user", content=request.message))

    # 4. Generate response from active Target Provider (Ollama / Grok / Mock)
    try:
        raw_response = await target_module.active_provider.generate_response(
            messages=full_messages,
            system_prompt=system_prompt,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 1024
        )
    except Exception as e:
        logger.error(f"Target provider generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Target chatbot model generation failed: {str(e)}"
        )

    # 5. Evaluate Output Guardrail Hook
    guardrail_info = GuardrailTriggeredInfo(triggered=False)
    final_response = raw_response

    if not request.bypass_guardrails:
        output_guard_result = target_module.guardrail_engine.inspect_output(raw_response)
        if output_guard_result.triggered:
            guardrail_info = output_guard_result
            final_response = output_guard_result.reason or "Response suppressed by safety guardrails."

    latency_ms = (time.time() - start_time) * 1000

    return ChatResponse(
        response=final_response,
        model=target_module.active_provider.model_name,
        provider=target_module.active_provider.__class__.__name__,
        prompt_hash=prompt_hash,
        guardrail_info=guardrail_info,
        latency_ms=round(latency_ms, 2),
        total_messages=len(full_messages)
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Returns service health status, active provider, prompt hash, and rule counts."""
    prompt, prompt_hash = target_module.prompt_manager.get_prompt()
    guardrails = target_module.guardrail_engine.config

    return HealthResponse(
        status="healthy",
        provider=target_module.active_provider.__class__.__name__,
        model=target_module.active_provider.model_name,
        system_prompt_hash=prompt_hash,
        system_prompt_char_count=len(prompt),
        guardrails_enabled=guardrails.enabled,
        input_rules_count=len(guardrails.input_rules),
        output_rules_count=len(guardrails.output_rules),
        total_requests_served=_request_counter
    )


@router.post("/reload", response_model=ReloadResponse)
async def force_reload():
    """Forces an immediate reload of system_prompt.txt and guardrails.json from disk."""
    _, prompt_hash, prompt_changed = target_module.prompt_manager.reload()
    in_count, out_count = target_module.guardrail_engine.reload()

    return ReloadResponse(
        status="success",
        reloaded_prompt=True,
        reloaded_guardrails=True,
        prompt_hash=prompt_hash,
        input_rules_count=in_count,
        output_rules_count=out_count
    )


@router.get("/prompt")
async def get_system_prompt():
    """Returns current system prompt content and hash."""
    prompt, prompt_hash = target_module.prompt_manager.get_prompt()
    return {"prompt": prompt, "hash": prompt_hash}


@router.post("/prompt")
async def update_system_prompt(payload: dict):
    """Directly updates system_prompt.txt (hot-reloadable patch applicator)."""
    new_prompt = payload.get("prompt")
    if not new_prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' field in payload")

    prompt, prompt_hash = target_module.prompt_manager.update_prompt(new_prompt)
    return {"status": "updated", "prompt": prompt, "hash": prompt_hash}


@router.get("/guardrails", response_model=GuardrailsConfig)
async def get_guardrails():
    """Returns active guardrails configuration and rules."""
    return target_module.guardrail_engine.config


@router.post("/guardrails/rules", response_model=GuardrailsConfig)
async def add_guardrail_rule(rule: GuardrailRule):
    """Dynamically registers a new input guardrail rule."""
    target_module.guardrail_engine.add_input_rule(rule)
    return target_module.guardrail_engine.config


@router.delete("/guardrails/rules/{rule_id}")
async def delete_guardrail_rule(rule_id: str):
    """Deletes an existing guardrail rule by ID."""
    removed = target_module.guardrail_engine.remove_rule(rule_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
    return {"status": "deleted", "rule_id": rule_id}


@router.post("/provider")
async def switch_provider(payload: ProviderSwitchRequest):
    """Switches the active LLM backend provider at runtime (mock, ollama, grok)."""
    try:
        new_prov = target_module.create_provider(
            provider_name=payload.provider,
            model_name=payload.model,
            base_url=payload.base_url,
            api_key=payload.api_key
        )
        target_module.active_provider = new_prov
        return {
            "status": "switched",
            "provider": new_prov.__class__.__name__,
            "model": new_prov.model_name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed switching provider: {str(e)}")
