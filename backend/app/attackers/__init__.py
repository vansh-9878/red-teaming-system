import logging
from typing import Dict, List, Optional
from app.core.model_config import model_config_manager
from app.attackers.base import BaseAttackerAgent
from app.attackers.persona_agent import PersonaAgent
from app.attackers.persuasion_agent import PersuasionAgent
from app.attackers.escalation_agent import EscalationAgent
from app.attackers.obfuscation_agent import ObfuscationAgent
from app.target.base import BaseTargetProvider
import app.target as target_module

logger = logging.getLogger(__name__)


class AttackerSquad:
    """
    Registry and lifecycle coordinator for the 4 core literature-grounded specialist attacker agents.
    Uses model_config.json's 'attacker_agents' provider and model.
    """

    def __init__(self, llm_provider: Optional[BaseTargetProvider] = None):
        self.llm_provider = llm_provider
        self._agents: Dict[str, BaseAttackerAgent] = {}
        self.initialize_squad()

    def _resolve_provider(self) -> BaseTargetProvider:
        if self.llm_provider:
            return self.llm_provider
        # Instantiate from model_config.json's attacker_agents section
        cfg = model_config_manager.config.attacker_agents
        return target_module.create_provider(
            provider_name=cfg.provider,
            model_name=cfg.model,
            base_url=cfg.base_url,
            api_key=cfg.api_key
        )

    def initialize_squad(self) -> None:
        """Initializes the 4 specialist agents with their configured model provider."""
        provider = self._resolve_provider()
        self._agents = {
            "persona": PersonaAgent(llm_provider=provider),
            "persuasion": PersuasionAgent(llm_provider=provider),
            "escalation": EscalationAgent(llm_provider=provider),
            "obfuscation": ObfuscationAgent(llm_provider=provider),
        }
        logger.info(f"[AttackerSquad] Initialized {len(self._agents)} specialist agents with {provider.__class__.__name__} ({provider.model_name}).")

    def get_agent(self, identifier: str) -> Optional[BaseAttackerAgent]:
        """Looks up an agent by category or agent_id (e.g. 'persona' or 'agent_persona')."""
        key = identifier.lower().replace("agent_", "").strip()
        return self._agents.get(key)

    @property
    def agents(self) -> Dict[str, BaseAttackerAgent]:
        return self._agents

    def list_agents(self) -> List[Dict[str, str]]:
        return [
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "category": a.category,
                "description": a.description,
                "model": a.llm_provider.model_name if a.llm_provider else "default"
            }
            for a in self._agents.values()
        ]

    def reset_all_memories(self) -> None:
        """Clears memory logs across all squad agents."""
        for agent in self._agents.values():
            agent.memory.clear()
            if isinstance(agent, EscalationAgent):
                agent.reset_conversation()
        logger.info("[AttackerSquad] Reset episodic memories across all agents.")


# Global Attacker Squad singleton instance
attacker_squad = AttackerSquad()
