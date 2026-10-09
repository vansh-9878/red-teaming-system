"""
Module 6: Patch Generator Engine for SentinelLoop.
Converts structured diagnoses into live, class-level security patches:
- System-Prompt Patches: Appended to system_prompt.txt and hot-reloaded automatically.
- Input-Guardrail Patches: Injected into guardrails.json as class-level regex/delimiter/semantic rules.
- Adaptive LLM Synthesis: Connects to Grok/Groq to dynamically author novel, tailored defenses.
- Audit Logging: Tracks all patches in patch_audit_log.json for rollback & provenance.
"""
import json
import uuid
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
import app.target as target_module
from app.schemas.diagnostic import DiagnosisResult
from app.schemas.chat import GuardrailRule
from app.schemas.patch import (
    PatchResult,
    BatchPatchResponse,
    PatchStatusResponse
)
from app.patcher.prompt_templates import (
    SYSTEM_PROMPT_PATCH_TYPES,
    select_system_prompt_patch
)
from app.patcher.guardrail_templates import (
    select_input_guardrail_patch,
    build_delimiter_guardrail_rule,
    build_structural_regex_guardrail_rule,
    build_semantic_similarity_guardrail_rule
)
from app.patcher.audit_logger import PatchAuditLogger
from app.patcher.llm_patcher import AdaptiveLLMPatcher

logger = logging.getLogger(__name__)

INITIAL_BASELINE_PROMPT = (
    "You are a helpful, polite, and compliant general-purpose AI assistant.\n"
    "You answer user questions accurately, cheerfully, and helpfully while adhering to safety and operational guidelines.\n"
)


class PatchEngine:
    """
    Live Adaptive Patch Generation and Enforcement Engine.
    Applies class-level defenses live with zero server restarts.
    """

    def __init__(
        self,
        audit_logger: Optional[PatchAuditLogger] = None,
        llm_patcher: Optional[AdaptiveLLMPatcher] = None
    ):
        self.audit_logger = audit_logger or PatchAuditLogger()
        self.llm_patcher = llm_patcher or AdaptiveLLMPatcher()

    async def generate_and_apply_patch_async(
        self,
        diagnosis: DiagnosisResult,
        patch_type_override: Optional[str] = None,
        dry_run: bool = False,
        use_llm: bool = True
    ) -> PatchResult:
        """
        Async implementation of patch generation and application.
        Attempts adaptive synthesis via Grok/Groq LLM first, falling back to class-level templates.
        """
        patch_id = f"patch_{uuid.uuid4().hex[:10]}"
        timestamp = time.time()
        category = diagnosis.category
        layer = diagnosis.layer
        evidence = diagnosis.evidence
        probe = diagnosis.triggering_probe

        curr_prompt, prompt_hash = target_module.prompt_manager.get_prompt()
        active_guardrails = [r.model_dump() for r in target_module.guardrail_engine.config.input_rules]
        patch_history = self.audit_logger.get_all_patches()

        synthesized_by = "template_engine"
        llm_patch_data = None

        # 1. Attempt Adaptive LLM Patch Synthesis (Grok / Groq)
        if use_llm and not patch_type_override:
            try:
                llm_patch_data = await self.llm_patcher.synthesize_adaptive_patch(
                    diagnosis=diagnosis,
                    current_system_prompt=curr_prompt,
                    active_guardrails=active_guardrails,
                    patch_history=patch_history,
                    target_response=diagnosis.target_response
                )
            except Exception as e:
                logger.warning(f"[PatchEngine] LLM patcher call failed: {e}. Falling back to templates.")
                llm_patch_data = None

        # 2. Apply System-Prompt Patch
        target_layer_decision = (llm_patch_data.get("target_layer") if llm_patch_data else layer)

        if target_layer_decision == "system_prompt":
            if llm_patch_data and "patch_content" in llm_patch_data:
                ptype = llm_patch_data.get("patch_type", "adaptive_llm_prompt_constraint")
                patch_content = str(llm_patch_data["patch_content"]).strip()
                synthesized_by = f"{self.llm_patcher.provider}_llm"
            elif patch_type_override and patch_type_override in SYSTEM_PROMPT_PATCH_TYPES:
                ptype = patch_type_override
                patch_content = SYSTEM_PROMPT_PATCH_TYPES[ptype]["template"].strip()
            else:
                ptype, patch_content = select_system_prompt_patch(category, evidence)
                patch_content = patch_content.strip()

            # Ensure directive is appended without duplicate repetition
            if patch_content not in curr_prompt:
                new_prompt = f"{curr_prompt.strip()}\n\n{patch_content}"
            else:
                new_prompt = curr_prompt

            new_hash = prompt_hash
            if not dry_run:
                _, new_hash = target_module.prompt_manager.update_prompt(new_prompt)
                logger.info(f"[PatchEngine] Applied system-prompt patch ({synthesized_by}: '{ptype}') -> New Hash: {new_hash}")

            result = PatchResult(
                patch_id=patch_id,
                timestamp=timestamp,
                patch_type=ptype,
                target_layer="system_prompt",
                target_file="system_prompt.txt",
                patch_content=patch_content,
                triggering_diagnosis=diagnosis.model_dump(),
                status="applied" if not dry_run else "dry_run",
                synthesized_by=synthesized_by,
                system_prompt_hash=new_hash,
                active_guardrail_rules_count=len(target_module.guardrail_engine.config.input_rules),
                message=f"Live system-prompt patch '{ptype}' ({synthesized_by}) applied successfully."
            )

        # 3. Apply Input-Guardrail Patch
        else:
            if llm_patch_data and "patch_content" in llm_patch_data:
                ptype = llm_patch_data.get("patch_type", "adaptive_llm_guardrail_rule")
                raw_rule = llm_patch_data["patch_content"]
                synthesized_by = f"{self.llm_patcher.provider}_llm"
                
                # Parse rule content if JSON string or dict
                if isinstance(raw_rule, str):
                    try:
                        rule_dict = json.loads(raw_rule)
                    except Exception:
                        rule_dict = {
                            "id": f"rule_llm_{uuid.uuid4().hex[:8]}",
                            "type": "regex",
                            "pattern": raw_rule,
                            "description": f"Adaptive {category} guardrail generated by LLM",
                            "action": "block",
                            "refusal_message": "Request blocked by adaptive security policy."
                        }
                elif isinstance(raw_rule, dict):
                    rule_dict = raw_rule
                else:
                    rule_dict = {
                        "id": f"rule_llm_{uuid.uuid4().hex[:8]}",
                        "type": "regex",
                        "pattern": str(raw_rule),
                        "description": f"Adaptive {category} guardrail generated by LLM",
                        "action": "block",
                        "refusal_message": "Request blocked by adaptive security policy."
                    }
                
                if "id" not in rule_dict:
                    rule_dict["id"] = f"rule_llm_{uuid.uuid4().hex[:8]}"
                if "type" not in rule_dict:
                    rule_dict["type"] = "regex"
                if "action" not in rule_dict:
                    rule_dict["action"] = "block"
                if "refusal_message" not in rule_dict:
                    rule_dict["refusal_message"] = "I cannot assist with that request as it violates safety policies."
                
                rule = GuardrailRule(**rule_dict)

            elif patch_type_override == "input_delimiter_guardrail":
                ptype, rule = build_delimiter_guardrail_rule(category)
            elif patch_type_override == "input_structural_regex":
                ptype, rule = build_structural_regex_guardrail_rule(category, diagnosis.detected_patterns)
            elif patch_type_override == "input_semantic_filter":
                ptype, rule = build_semantic_similarity_guardrail_rule(category, probe)
            else:
                ptype, rule = select_input_guardrail_patch(
                    category=category,
                    triggering_probe=probe,
                    detected_patterns=diagnosis.detected_patterns
                )

            if not dry_run:
                target_module.guardrail_engine.add_input_rule(rule)
                logger.info(f"[PatchEngine] Injected live input-guardrail rule ({synthesized_by}): {rule.id} ({rule.type})")

            _, curr_hash = target_module.prompt_manager.get_prompt()
            active_rules_cnt = len(target_module.guardrail_engine.config.input_rules)

            result = PatchResult(
                patch_id=patch_id,
                timestamp=timestamp,
                patch_type=ptype,
                target_layer="input_guardrail",
                target_file="guardrails.json",
                patch_content=rule.model_dump_json(indent=2),
                triggering_diagnosis=diagnosis.model_dump(),
                status="applied" if not dry_run else "dry_run",
                synthesized_by=synthesized_by,
                system_prompt_hash=curr_hash,
                active_guardrail_rules_count=active_rules_cnt,
                message=f"Live input-guardrail rule '{rule.id}' ({ptype}, {synthesized_by}) deployed successfully."
            )

        # Log patch to persistent audit trail
        if not dry_run:
            self.audit_logger.log_patch(result)

        return result

    def generate_and_apply_patch(
        self,
        diagnosis: DiagnosisResult,
        patch_type_override: Optional[str] = None,
        dry_run: bool = False,
        use_llm: bool = True
    ) -> PatchResult:
        """
        Synchronous wrapper for generate_and_apply_patch_async.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In async context with active loop, create task or run in executor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(
                        asyncio.run,
                        self.generate_and_apply_patch_async(diagnosis, patch_type_override, dry_run, use_llm)
                    ).result()
            else:
                return loop.run_until_complete(
                    self.generate_and_apply_patch_async(diagnosis, patch_type_override, dry_run, use_llm)
                )
        except Exception:
            return asyncio.run(
                self.generate_and_apply_patch_async(diagnosis, patch_type_override, dry_run, use_llm)
            )

    async def apply_batch_patches_async(
        self,
        diagnoses: List[DiagnosisResult],
        dry_run: bool = False,
        use_llm: bool = True
    ) -> BatchPatchResponse:
        """
        Batch synthesizes and applies patches for multiple diagnoses from a campaign.
        """
        patches: List[PatchResult] = []
        sp_count = 0
        ig_count = 0

        for diag in diagnoses:
            patch_res = await self.generate_and_apply_patch_async(diag, dry_run=dry_run, use_llm=use_llm)
            patches.append(patch_res)
            if patch_res.target_layer == "system_prompt":
                sp_count += 1
            else:
                ig_count += 1

        return BatchPatchResponse(
            total_requested=len(diagnoses),
            total_applied=len(patches),
            system_prompt_patches=sp_count,
            input_guardrail_patches=ig_count,
            patches=patches
        )

    def apply_batch_patches(
        self,
        diagnoses: List[DiagnosisResult],
        dry_run: bool = False,
        use_llm: bool = True
    ) -> BatchPatchResponse:
        """
        Synchronous wrapper for apply_batch_patches_async.
        """
        try:
            return asyncio.run(self.apply_batch_patches_async(diagnoses, dry_run, use_llm))
        except Exception:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(
                    asyncio.run,
                    self.apply_batch_patches_async(diagnoses, dry_run, use_llm)
                ).result()

    def rollback_patch(self, patch_id: str) -> bool:
        """
        Rolls back a specific patch by ID.
        """
        patch_record = self.audit_logger.get_patch_by_id(patch_id)
        if not patch_record:
            logger.warning(f"[PatchEngine] Rollback requested for unknown patch ID: {patch_id}")
            return False

        target_layer = patch_record.get("target_layer")
        content = patch_record.get("patch_content", "")

        if target_layer == "system_prompt":
            curr_prompt, _ = target_module.prompt_manager.get_prompt()
            updated_prompt = curr_prompt.replace(content, "").strip()
            target_module.prompt_manager.update_prompt(updated_prompt)
            self.audit_logger.update_patch_status(patch_id, "rolled_back")
            logger.info(f"[PatchEngine] Rolled back system prompt patch: {patch_id}")
            return True

        elif target_layer == "input_guardrail":
            try:
                rule_dict = json.loads(content)
                rule_id = rule_dict.get("id")
                if rule_id:
                    removed = target_module.guardrail_engine.remove_rule(rule_id)
                    if removed:
                        self.audit_logger.update_patch_status(patch_id, "rolled_back")
                        logger.info(f"[PatchEngine] Rolled back guardrail rule: {rule_id}")
                        return True
            except Exception as e:
                logger.error(f"[PatchEngine] Error parsing guardrail rule during rollback: {e}")

        return False

    def rollback_to_baseline(self) -> bool:
        """
        Reverts system_prompt.txt to initial clean baseline, clears all guardrail rules,
        and wipes all patches and verification logs from history.
        """
        try:
            target_module.prompt_manager.update_prompt(INITIAL_BASELINE_PROMPT)
            target_module.guardrail_engine._config.input_rules = []
            target_module.guardrail_engine._config.output_rules = []
            target_module.guardrail_engine.save_config()
            target_module.guardrail_engine.reload()

            # Clear persistent patch audit log
            self.audit_logger.clear()

            # Clear persistent verification / RASR history
            try:
                from app.verifier import verification_log_manager
                verification_log_manager.reset()
            except Exception:
                pass

            logger.info("[PatchEngine] Successfully rolled back target system to initial baseline, cleared patches and guardrails history.")
            return True
        except Exception as e:
            logger.error(f"[PatchEngine] Failed rollback to baseline: {e}")
            return False

    def get_status(self) -> PatchStatusResponse:
        """
        Returns live telemetry on active prompt hash, guardrail rules, and applied patch history.
        """
        prompt, prompt_hash = target_module.prompt_manager.get_prompt()
        config = target_module.guardrail_engine.config
        all_patches_raw = self.audit_logger.get_all_patches()
        
        recent = [PatchResult(**p) for p in all_patches_raw[-10:]]

        return PatchStatusResponse(
            total_patches_applied=len(all_patches_raw),
            system_prompt_hash=prompt_hash,
            system_prompt_char_count=len(prompt),
            input_guardrails_count=len(config.input_rules),
            output_guardrails_count=len(config.output_rules),
            guardrails_enabled=config.enabled,
            recent_patches=recent
        )
