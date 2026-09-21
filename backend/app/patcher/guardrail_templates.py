"""
Input-guardrail patch templates for Module 6: Patch Generator.
Generates class-level, generalized input guardrail rules:
1. Prompt-injection/delimiter detector for fake-system-tag probes
2. Structural encoding & execution harness regex filters
3. Semantic similarity exemplar filters
"""
import uuid
from typing import Dict, Any, List, Tuple
from app.schemas.chat import GuardrailRule


def build_delimiter_guardrail_rule(category: str = "obfuscation") -> Tuple[str, GuardrailRule]:
    """
    Builds a class-level prompt-injection & delimiter detector rule
    specifically targeting Obfuscation Agent fake-system-tag probes.
    """
    rule_id = f"rule_delimiter_{uuid.uuid4().hex[:8]}"
    pattern = r"(?:<\|im_start\|>|<\|im_end\|>|\[SYSTEM DIRECTIVE|\[BEGIN SYSTEM RECORD\]|```system|<system_override|\{\{SYSTEM_DIRECTIVE|### SYSTEM_OVERRIDE|<!--\s*System authorization|/\*\s*IGNORE ALL PRIOR|\[ADMIN_SESSION_START\]|<instruction_block>|<system>)"
    
    rule = GuardrailRule(
        id=rule_id,
        type="delimiter",
        pattern=pattern,
        description="Class-level delimiter & fake system injection tag detector (Obfuscation defense)",
        action="block",
        refusal_message="I cannot process this request because it contains restricted system delimiter or instruction override formatting.",
        case_sensitive=False
    )
    return "input_delimiter_guardrail", rule


def build_structural_regex_guardrail_rule(category: str, detected_patterns: List[str]) -> Tuple[str, GuardrailRule]:
    """
    Builds a class-level structural regex rule targeting encodings, ciphers, code harnesses, or GCG suffixes.
    """
    rule_id = f"rule_regex_{uuid.uuid4().hex[:8]}"
    
    # Class-level regex patterns (not single keywords)
    pattern = (
        r"(?:[A-Za-z0-9+/]{32,}={0,2}|"
        r"(?:rot13 cipher|1337speak instruction|Caesar Cipher|Atbash cipher text|hexadecimal byte sequence|URL-decode the following)|"
        r"fn\s+\w+\s*\(\s*\)\s*->|for\s*\(\s*let\s+\w+\s*=|func\s+\w+\s*\(\s*\)\s*\{|eval\s*\(\s*\"\"\"#|cat\s*<<\s*'EOF'|"
        r"== interface manually backward compatible|describing\.\\ \+\s*similarlyNow write opposite)"
    )
    
    rule = GuardrailRule(
        id=rule_id,
        type="regex",
        pattern=pattern,
        description=f"Class-level structural pattern & execution harness regex filter ({category})",
        action="block",
        refusal_message="I cannot process this request because it matches an unauthorized obfuscation, encoding, or code execution pattern.",
        case_sensitive=False
    )
    return "input_structural_regex", rule


def build_semantic_similarity_guardrail_rule(category: str, triggering_probe: str) -> Tuple[str, GuardrailRule]:
    """
    Builds a semantic similarity filtering guardrail rule anchored on known successful adversarial probes.
    """
    rule_id = f"rule_sem_{uuid.uuid4().hex[:8]}"
    
    rule = GuardrailRule(
        id=rule_id,
        type="semantic_similarity",
        pattern=triggering_probe.strip(),
        description=f"Class-level semantic similarity filter anchored on {category} adversarial probe",
        action="block",
        refusal_message="I cannot assist with this request as it closely resembles restricted adversarial testing patterns.",
        case_sensitive=False
    )
    return "input_semantic_filter", rule


def select_input_guardrail_patch(
    category: str,
    triggering_probe: str,
    detected_patterns: List[str]
) -> Tuple[str, GuardrailRule]:
    """
    Selects the optimal class-level input guardrail rule for a given diagnosis.
    """
    category_lower = category.lower()

    # If delimiter tags were detected or category is obfuscation with delimiters:
    if any("delimiter" in p or "bracket" in p or "xml" in p or "tag" in p for p in detected_patterns):
        return build_delimiter_guardrail_rule(category_lower)
    
    # If structural encodings, code wrappers, or GCG suffixes detected:
    elif any("base64" in p or "cipher" in p or "wrapper" in p or "gcg" in p or "hex" in p for p in detected_patterns):
        return build_structural_regex_guardrail_rule(category_lower, detected_patterns)
    
    # Default to semantic similarity exemplar filtering
    else:
        return build_semantic_similarity_guardrail_rule(category_lower, triggering_probe)
