"""
Unit tests for Module 4: Coordinator (UCB Multi-Armed Bandit Scheduler & Vulnerability Fingerprints).
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.coordinator.bandit import UCBBanditScheduler
from app.coordinator.fingerprint import FingerprintManager
from app.coordinator import coordinator_engine


@pytest.fixture
def client():
    return TestClient(app)


def test_bandit_cold_start_initialization():
    """Verify Cold-Start initializes all arms while honoring Escalation multi-turn trajectory bursts."""
    scheduler = UCBBanditScheduler(novelty_frequency=100, starvation_threshold=100, escalation_burst_length=3)
    expected_arms = {"persona", "persuasion", "escalation", "obfuscation"}

    pulled_arms = []
    # 3 single arms + 3 consecutive escalation turns = 6 total initial turns
    for _ in range(6):
        decision = scheduler.select_next_agent()
        pulled_arms.append(decision.chosen_agent)
        scheduler.update_reward(decision.chosen_agent, reward=0.2)

    assert set(pulled_arms) == expected_arms
    assert scheduler.total_rounds == 6


def test_bandit_ucb_exploitation():
    """Verify that arms with higher rewards receive higher UCB scores and are exploited."""
    scheduler = UCBBanditScheduler(novelty_frequency=100, starvation_threshold=100, escalation_burst_length=1)

    # 1. Complete cold start (with burst length=1 for pure single-turn test)
    for _ in range(4):
        decision = scheduler.select_next_agent()
        reward = 0.95 if decision.chosen_agent == "obfuscation" else 0.1
        scheduler.update_reward(decision.chosen_agent, reward=reward, is_jailbreak=(reward > 0.6))

    # 2. Next decision should be UCB optimal on the high-performing arm
    next_decision = scheduler.select_next_agent()
    assert next_decision.selection_reason == "ucb_optimal"
    assert next_decision.chosen_agent == "obfuscation"
    assert next_decision.bandit_weights["obfuscation"] > next_decision.bandit_weights["persona"]


def test_novelty_injection_rule():
    """Verify Novelty-Injection (STAR 2026) forces exploration when an arm is starved."""
    # Set starvation threshold to 3
    scheduler = UCBBanditScheduler(novelty_frequency=100, starvation_threshold=3, escalation_burst_length=1)

    # Complete cold start
    for _ in range(4):
        decision = scheduler.select_next_agent()
        scheduler.update_reward(decision.chosen_agent, reward=0.8 if decision.chosen_agent == "persona" else 0.1)

    # Heavily exploit persona for 3 consecutive rounds
    for _ in range(3):
        decision = scheduler.select_next_agent()
        scheduler.update_reward("persona", reward=0.9)

    # Now the other arms (persuasion, escalation, obfuscation) are starved >= 3 rounds
    novelty_decision = scheduler.select_next_agent()
    assert novelty_decision.selection_reason == "novelty_injection"
    assert "Novelty-Injection" in novelty_decision.explanation
    assert novelty_decision.chosen_agent in ["persuasion", "escalation", "obfuscation"]


def test_escalation_multi_turn_trajectory_locking():
    """Verify that when Escalation is selected, it executes 3 consecutive turns before switching."""
    scheduler = UCBBanditScheduler(novelty_frequency=100, starvation_threshold=100, escalation_burst_length=3)
    scheduler.reset()

    # 1. First arm is persona
    d0 = scheduler.select_next_agent()
    scheduler.update_reward(d0.chosen_agent, 0.1)

    # 2. Second arm is persuasion
    d1 = scheduler.select_next_agent()
    scheduler.update_reward(d1.chosen_agent, 0.1)

    # 3. Third arm is escalation (Turn 1 of burst)
    d2 = scheduler.select_next_agent()
    assert d2.chosen_agent == "escalation"
    assert d2.selection_reason == "cold_start"
    scheduler.update_reward("escalation", 0.2)

    # 4. MUST continue Escalation (Turn 2 of burst)
    d3 = scheduler.select_next_agent()
    assert d3.chosen_agent == "escalation"
    assert "trajectory_burst_turn_2" in d3.selection_reason
    scheduler.update_reward("escalation", 0.3)

    # 5. MUST continue Escalation (Turn 3 of burst)
    d4 = scheduler.select_next_agent()
    assert d4.chosen_agent == "escalation"
    assert "trajectory_burst_turn_3" in d4.selection_reason
    scheduler.update_reward("escalation", 0.3)

    # 6. After 3 turns, trajectory lock is released and cold-start continues for obfuscation
    assert scheduler.locked_agent is None
    d5 = scheduler.select_next_agent()
    assert d5.chosen_agent == "obfuscation"
    assert d5.selection_reason == "cold_start"



def test_vulnerability_fingerprint_generation_and_persistence(tmp_path):
    """Verify computing and saving vulnerability fingerprints for a target model."""
    custom_storage = tmp_path / "test_fingerprints.json"
    mgr = FingerprintManager(storage_path=custom_storage)
    scheduler = UCBBanditScheduler()

    # Simulate campaign
    scheduler.update_reward("persona", reward=0.2, is_jailbreak=False)
    scheduler.update_reward("obfuscation", reward=0.85, is_jailbreak=True)
    scheduler.update_reward("persuasion", reward=0.1, is_jailbreak=False)
    scheduler.update_reward("escalation", reward=0.4, is_jailbreak=False)

    fp = mgr.compute_fingerprint(
        target_model="test-model-70b",
        target_provider="MockProvider",
        arms=scheduler.arms,
        total_rounds=4,
        system_prompt_hash="abc123hash"
    )

    assert fp.target_model == "test-model-70b"
    assert fp.total_campaign_rounds == 4
    assert fp.overall_asr == 0.25  # 1 win out of 4
    assert fp.dominant_vulnerability == "obfuscation"
    assert fp.category_breakdown["obfuscation"]["severity_rating"] == "Critical"

    # Test saving and retrieving
    mgr.save_fingerprint(fp)
    saved_data = mgr.list_fingerprints()
    key = "MockProvider::test-model-70b"
    assert key in saved_data
    assert saved_data[key]["dominant_vulnerability"] == "obfuscation"


def test_coordinator_api_endpoints(client):
    """Verify Coordinator REST API routes."""
    # Reset
    res_reset = client.post("/coordinator/reset")
    assert res_reset.status_code == 200

    # Select next agent
    res_select = client.post("/coordinator/select")
    assert res_select.status_code == 200
    data = res_select.json()
    assert "chosen_agent" in data
    assert "selection_reason" in data
    assert "bandit_weights" in data

    chosen = data["chosen_agent"]

    # Update reward
    res_update = client.post("/coordinator/update", json={
        "agent_id": chosen,
        "reward": 0.75,
        "is_jailbreak": True
    })
    assert res_update.status_code == 200
    arm_state = res_update.json()
    assert arm_state["pulls"] == 1
    assert arm_state["mean_reward"] == 0.75
    assert arm_state["win_count"] == 1

    # Get state
    res_state = client.get("/coordinator/state")
    assert res_state.status_code == 200
    state_data = res_state.json()
    assert state_data["total_rounds"] == 1
    assert state_data["arms"][chosen]["pulls"] == 1

    # Generate Fingerprint
    res_fp = client.post("/coordinator/fingerprints")
    assert res_fp.status_code == 200
    fp_data = res_fp.json()
    assert fp_data["total_campaign_rounds"] == 1
    assert fp_data["dominant_vulnerability"] == chosen

    # List Fingerprints
    res_list_fp = client.get("/coordinator/fingerprints")
    assert res_list_fp.status_code == 200
