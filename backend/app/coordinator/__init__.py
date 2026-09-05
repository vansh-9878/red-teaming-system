"""
Coordinator Module for SentinelLoop:
Exposes UCB Multi-Armed Bandit Scheduler and Vulnerability Fingerprint Manager.
"""
import logging
from typing import Optional, Dict, Any
from app.coordinator.bandit import UCBBanditScheduler
from app.coordinator.fingerprint import FingerprintManager, fingerprint_manager
from app.schemas.coordinator import CoordinatorDecision, BanditArmState, VulnerabilityFingerprint

logger = logging.getLogger(__name__)


class CoordinatorEngine:
    """
    Coordinator Engine coordinating the UCB Bandit, specialist agents, and campaign lifecycle.
    """

    def __init__(
        self,
        exploration_constant: float = 1.414,
        novelty_frequency: int = 4,
        starvation_threshold: int = 4,
    ):
        self.scheduler = UCBBanditScheduler(
            exploration_constant=exploration_constant,
            novelty_frequency=novelty_frequency,
            starvation_threshold=starvation_threshold
        )
        self.fingerprint_mgr = fingerprint_manager

    def select_agent(self) -> CoordinatorDecision:
        """Selects next agent via UCB policy + Novelty Injection."""
        return self.scheduler.select_next_agent()

    def update_reward(self, agent_id: str, reward: float, is_jailbreak: bool = False) -> BanditArmState:
        """Updates bandit with round reward signal."""
        return self.scheduler.update_reward(agent_id=agent_id, reward=reward, is_jailbreak=is_jailbreak)

    def generate_and_save_fingerprint(
        self,
        target_model: str,
        target_provider: str,
        system_prompt_hash: Optional[str] = None
    ) -> VulnerabilityFingerprint:
        """Computes and saves vulnerability fingerprint from current campaign."""
        fp = self.fingerprint_mgr.compute_fingerprint(
            target_model=target_model,
            target_provider=target_provider,
            arms=self.scheduler.arms,
            total_rounds=self.scheduler.total_rounds,
            system_prompt_hash=system_prompt_hash
        )
        self.fingerprint_mgr.save_fingerprint(fp)
        return fp

    def reset(self) -> None:
        """Resets the coordinator scheduler state."""
        self.scheduler.reset()


# Global Coordinator singleton instance
coordinator_engine = CoordinatorEngine()
