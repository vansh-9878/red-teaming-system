import os
import re
import json
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from app.schemas.chat import GuardrailRule, GuardrailsConfig, GuardrailTriggeredInfo

logger = logging.getLogger(__name__)


class GuardrailEngine:
    """
    Pluggable Guardrail Interception Hook Layer for Input and Output filtering.
    Dynamically loads and hot-reloads rules from guardrails.json.
    """

    def __init__(self, config_path: str):
        self.config_path = Path(config_path).resolve()
        self._config: GuardrailsConfig = GuardrailsConfig(enabled=True, input_rules=[], output_rules=[])
        self._last_mtime: float = 0.0
        self.ensure_file_exists()
        self.reload()

    def ensure_file_exists(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            default_data = {
                "enabled": True,
                "input_rules": [],
                "output_rules": []
            }
            self.config_path.write_text(json.dumps(default_data, indent=2), encoding="utf-8")

    def reload(self) -> Tuple[int, int]:
        try:
            mtime = os.path.getmtime(self.config_path)
            content = self.config_path.read_text(encoding="utf-8")
            data = json.loads(content)
            self._config = GuardrailsConfig(**data)
            self._last_mtime = mtime
            logger.info(
                f"[GuardrailEngine] Loaded {len(self._config.input_rules)} input rules, "
                f"{len(self._config.output_rules)} output rules (Enabled: {self._config.enabled})"
            )
            return len(self._config.input_rules), len(self._config.output_rules)
        except Exception as e:
            logger.error(f"[GuardrailEngine] Failed to load guardrail config: {e}")
            return len(self._config.input_rules), len(self._config.output_rules)

    def _check_mtime(self) -> None:
        try:
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime != self._last_mtime:
                self.reload()
        except Exception:
            pass

    @property
    def config(self) -> GuardrailsConfig:
        self._check_mtime()
        return self._config

    def _matches_rule(self, text: str, rule: GuardrailRule) -> bool:
        """Evaluates whether text violates a specific guardrail rule."""
        target_text = text if rule.case_sensitive else text.lower()
        pattern = rule.pattern if rule.case_sensitive else rule.pattern.lower()

        if rule.type == "keyword":
            return pattern in target_text

        elif rule.type == "regex":
            try:
                flags = 0 if rule.case_sensitive else re.IGNORECASE
                return bool(re.search(rule.pattern, text, flags))
            except Exception as err:
                logger.warning(f"Invalid regex rule {rule.id}: {err}")
                return False

        elif rule.type == "delimiter":
            # Detects delimiters and injection tags like <|im_start|>, [SYSTEM], ```system, etc.
            delimiters = [
                "<|im_start|>", "<|im_end|>", "[system]", "```system",
                "### instruction", "### system", "<system>", "</system>"
            ]
            if pattern:
                delimiters.append(pattern)
            return any(d in target_text for d in delimiters)

        elif rule.type in ("category_framing", "semantic_pattern"):
            # Substring / pattern check for specific framing idioms (e.g. DAN, pretend you are, hypothetically)
            return pattern in target_text

        elif rule.type == "semantic_similarity":
            # Semantic similarity matching against exemplar probe
            exemplar = pattern
            words_target = set(re.findall(r'\w+', target_text))
            words_exemplar = set(re.findall(r'\w+', exemplar))
            if not words_target or not words_exemplar:
                return False
            intersection = len(words_target & words_exemplar)
            union = len(words_target | words_exemplar)
            jaccard = intersection / union if union > 0 else 0.0
            overlap_ratio = intersection / min(len(words_target), len(words_exemplar))
            return jaccard >= 0.40 or overlap_ratio >= 0.60

        return False

    def inspect_input(self, text: str, history_texts: Optional[List[str]] = None) -> GuardrailTriggeredInfo:
        """
        Input Guardrail Hook:
        Checks the incoming message (and optionally history) against active input rules.
        """
        self._check_mtime()
        if not self._config.enabled or not self._config.input_rules:
            return GuardrailTriggeredInfo(triggered=False)

        # Inspect main message
        for rule in self._config.input_rules:
            if self._matches_rule(text, rule):
                logger.info(f"[GuardrailEngine] Input rule triggered: {rule.id} ({rule.type})")
                return GuardrailTriggeredInfo(
                    triggered=True,
                    rule_id=rule.id,
                    rule_type=rule.type,
                    rule_description=rule.description or f"Triggered rule pattern: {rule.pattern}",
                    stage="input",
                    reason=rule.refusal_message
                )

        # Optionally inspect multi-turn history if present
        if history_texts:
            full_context = " ".join(history_texts)
            for rule in self._config.input_rules:
                if self._matches_rule(full_context, rule):
                    logger.info(f"[GuardrailEngine] Input history triggered rule: {rule.id} ({rule.type})")
                    return GuardrailTriggeredInfo(
                        triggered=True,
                        rule_id=rule.id,
                        rule_type=rule.type,
                        rule_description=rule.description or f"Triggered rule in history: {rule.pattern}",
                        stage="input",
                        reason=rule.refusal_message
                    )

        return GuardrailTriggeredInfo(triggered=False)

    def inspect_output(self, text: str) -> GuardrailTriggeredInfo:
        """
        Output Guardrail Hook:
        Checks the generated model response against active output rules.
        """
        self._check_mtime()
        if not self._config.enabled or not self._config.output_rules:
            return GuardrailTriggeredInfo(triggered=False)

        for rule in self._config.output_rules:
            if self._matches_rule(text, rule):
                logger.info(f"[GuardrailEngine] Output rule triggered: {rule.id}")
                return GuardrailTriggeredInfo(
                    triggered=True,
                    rule_id=rule.id,
                    rule_type=rule.type,
                    rule_description=rule.description or f"Output triggered rule pattern: {rule.pattern}",
                    stage="output",
                    reason=rule.refusal_message
                )

        return GuardrailTriggeredInfo(triggered=False)

    def add_input_rule(self, rule: GuardrailRule) -> None:
        """Dynamically appends a new input rule and persists to disk."""
        self._check_mtime()
        # Remove existing rule with same ID if present
        self._config.input_rules = [r for r in self._config.input_rules if r.id != rule.id]
        self._config.input_rules.append(rule)
        self.save_config()

    def remove_rule(self, rule_id: str) -> bool:
        """Removes a rule by ID from both input and output lists."""
        self._check_mtime()
        orig_len = len(self._config.input_rules) + len(self._config.output_rules)
        self._config.input_rules = [r for r in self._config.input_rules if r.id != rule_id]
        self._config.output_rules = [r for r in self._config.output_rules if r.id != rule_id]
        new_len = len(self._config.input_rules) + len(self._config.output_rules)
        if orig_len != new_len:
            self.save_config()
            return True
        return False

    def save_config(self) -> None:
        """Persists the current in-memory rules to guardrails.json."""
        self.config_path.write_text(self._config.model_dump_json(indent=2), encoding="utf-8")
        self._last_mtime = os.path.getmtime(self.config_path)
