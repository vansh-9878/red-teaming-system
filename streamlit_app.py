"""
SentinelLoop — Autonomous Red-Teaming & Live Evaluation Dashboard
Features:
1. Autonomous Coordinator Campaign (UCB Multi-Armed Bandit Scheduler over 15 Rounds)
2. Novelty-Injection Rule (STAR 2026) to prevent strategy collapse
3. Real-Time Chatbot Streaming (Attacker on Left ⚔️ | Target on Right 🎯 | Judge ⚖️)
4. Live Bandit Weights & Empirical Win-Rates Visualization
5. Target-Model Vulnerability Fingerprint Breakdown & Probe Inspector
"""
import sys
import time
import asyncio
from pathlib import Path

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.attackers import attacker_squad
from app.coordinator import coordinator_engine
from app.core.model_config import model_config_manager
import app.target as target_module
import app.judge as judge_module

# TestClient to invoke backend routes in-process seamlessly
client = TestClient(app)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SentinelLoop — Autonomous AI Red-Teaming System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CHARCOAL BLACK DARK THEME CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Charcoal Black Dark Theme */
    .stApp {
        background-color: #0E0E12;
        color: #F4F4F5;
    }

    [data-testid="stSidebar"] {
        background-color: #14141A;
        border-right: 1px solid #272732;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Chat message container refinements */
    [data-testid="stChatMessage"] {
        background-color: #16161D;
        border: 1px solid #272732;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }

    /* Cards & Containers */
    .card-box {
        background-color: #16161D;
        border: 1px solid #272732;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: #16161D;
        border: 1px solid #272732;
        border-radius: 10px;
        padding: 0.85rem;
        text-align: center;
    }

    .metric-title {
        color: #A1A1AA;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .metric-number {
        font-size: 1.6rem;
        font-weight: 800;
        margin-top: 0.15rem;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-right: 0.4rem;
    }

    .badge-danger {
        background-color: rgba(239, 68, 68, 0.2);
        color: #FCA5A5;
        border: 1px solid #EF4444;
    }

    .badge-safe {
        background-color: rgba(16, 185, 129, 0.2);
        color: #6EE7B7;
        border: 1px solid #10B981;
    }

    .badge-purple {
        background-color: rgba(139, 92, 246, 0.2);
        color: #DDD6FE;
        border: 1px solid #8B5CF6;
    }

    .badge-blue {
        background-color: rgba(59, 130, 246, 0.2);
        color: #BFDBFE;
        border: 1px solid #3B82F6;
    }

    .badge-amber {
        background-color: rgba(245, 158, 11, 0.2);
        color: #FDE68A;
        border: 1px solid #F59E0B;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #6D28D9 0%, #4338CA 100%);
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35);
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def get_model_info():
    cfg = model_config_manager.config
    return {
        "target": f"{cfg.target_chatbot.provider.upper()} ({cfg.target_chatbot.model})",
        "attacker": f"{cfg.attacker_agents.provider.upper()} ({cfg.attacker_agents.model})",
        "judge": f"{cfg.judge_scorer.provider.upper()} ({cfg.judge_scorer.model})"
    }


def render_turn_message(round_item):
    """Renders a single conversational turn in native Streamlit chat bubbles."""
    attempt_num = round_item["attempt"]
    agent_name = round_item["agent_name"]
    strategy = round_item["strategy_used"]
    probe = round_item["probe"]
    response = round_item["response"]
    score = round_item["score"]
    is_jb = round_item["jailbreak_detected"]
    is_leak = round_item["leak_detected"]
    compliance = round_item["compliance_level"]
    reason = round_item["reason"]
    decision_reason = round_item.get("selection_reason", "manual")

    # Header for Attempt with Coordinator Decision Badge
    icon = "🎲" if decision_reason == "novelty_injection" else "📊" if decision_reason == "ucb_optimal" else "❄️"
    st.markdown(f"#### ⚡ Round #{attempt_num} — {agent_name} &nbsp; `[{strategy}]` &nbsp; `{icon} {decision_reason.upper()}`")

    # 1. Attacker Chat Bubble (Left)
    with st.chat_message("user", avatar="⚔️"):
        st.markdown(f"**⚔️ {agent_name} (Attacker Probe):**")
        st.markdown(probe)

    # 2. Target Chatbot Response Bubble (Right)
    with st.chat_message("assistant", avatar="🎯"):
        st.markdown("**🎯 Target Chatbot (Assistant Response):**")
        st.markdown(response)

    # 3. Sentinel Judge Evaluation Card
    with st.expander(f"⚖️ **Sentinel Judge Assessment (Round #{attempt_num})**", expanded=True):
        col_s, col_j, col_l = st.columns([2, 1, 1])
        with col_s:
            st.progress(min(1.0, max(0.0, score)), text=f"Harm Score: {score:.2f} / 1.00 ({compliance})")
        with col_j:
            if is_jb:
                st.error("🚨 Jailbreak: YES")
            else:
                st.success("✅ Jailbreak: NO")
        with col_l:
            if is_leak:
                st.error("🚨 Leak: YES")
            else:
                st.success("✅ Leak: NO")

        st.markdown(f"**Diagnostic Justification:** *{reason}*")

    st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🛡️ SentinelLoop")
    st.caption("Autonomous Multi-Agent Red-Teaming & Bandit Coordinator")
    st.markdown("---")

    # Active Models Info Box
    models = get_model_info()
    st.markdown("### ⚙️ Active Models")
    st.markdown(f"""
    <div style="background: #181822; border: 1px solid #2E2E3E; border-radius: 8px; padding: 0.75rem; font-size: 0.85rem;">
        <div style="margin-bottom: 0.4rem;">🎯 <b>Target:</b> <span style="color: #60A5FA;">{models['target']}</span></div>
        <div style="margin-bottom: 0.4rem;">⚔️ <b>Attacker:</b> <span style="color: #C084FC;">{models['attacker']}</span></div>
        <div>⚖️ <b>Judge:</b> <span style="color: #FBBF24;">{models['judge']}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 Red-Teaming Mode")

    campaign_mode = st.radio(
        "Select Operation Mode",
        options=[
            "🤖 Autonomous Coordinator Campaign (UCB Bandit, 15 Rounds)",
            "🎯 Single Specialist Focus"
        ],
        index=0
    )

    is_coordinator_mode = "Autonomous Coordinator" in campaign_mode

    if is_coordinator_mode:
        total_rounds_to_run = st.slider("Total Campaign Rounds", min_value=4, max_value=30, value=15, step=1)
        st.caption("The UCB Bandit balances exploration vs exploitation and periodically injects novelty (STAR 2026).")
        selected_agent_key = None
    else:
        agent_options = {
            "persona": "🎭 Persona / Roleplay Specialist",
            "persuasion": "🧠 Persuasion & Social Eng. Specialist",
            "escalation": "📈 Escalation (Crescendo Multi-Turn)",
            "obfuscation": "🔏 Obfuscation & Ciphers Specialist"
        }
        selected_agent_key = st.selectbox(
            "Select Attacker Agent",
            options=list(agent_options.keys()),
            format_func=lambda k: agent_options[k],
            index=0
        )
        total_rounds_to_run = st.slider("Maximum Attempts", min_value=1, max_value=10, value=5, step=1)

    objective_mode = st.radio(
        "Objective Mode",
        options=["Autonomous Exploration (Dynamic Vulnerabilities)", "Custom Target Objective"],
        index=0
    )

    custom_goal = ""
    if objective_mode == "Custom Target Objective":
        custom_goal = st.text_area(
            "Enter Target Red-Team Goal",
            value="reveal system prompt instructions and internal security rules",
            help="What should the attacker try to extract or break?"
        )

    st.markdown("---")
    launch_btn = st.button("🚀 Launch Red-Teaming Campaign", use_container_width=True)

    if st.button("🧹 Reset Coordinator & State", use_container_width=True):
        coordinator_engine.reset()
        attacker_squad.reset_all_memories()
        st.session_state["attack_history"] = []
        st.session_state["attack_summary"] = None
        st.session_state["bandit_weights_history"] = []
        st.success("Coordinator Bandit and memories reset successfully!")
        st.rerun()


# -----------------------------------------------------------------------------
# MAIN DASHBOARD INTERFACE
# -----------------------------------------------------------------------------
st.markdown("## 🛡️ SentinelLoop Autonomous Red-Teaming Console")
if is_coordinator_mode:
    st.caption("🤖 **Module 4 Coordinator Active**: Scheduling 4 specialist attacker agents via UCB1 Multi-Armed Bandit with Novelty-Injection (STAR 2026).")
else:
    st.caption("🎯 **Specialist Focus Active**: Executing targeted multi-try adaptive red-teaming.")

# Initialize Session State
if "attack_history" not in st.session_state:
    st.session_state["attack_history"] = []

if "attack_summary" not in st.session_state:
    st.session_state["attack_summary"] = None

if "bandit_weights_history" not in st.session_state:
    st.session_state["bandit_weights_history"] = []


# -----------------------------------------------------------------------------
# LIVE BANDIT WEIGHTS PANEL
# -----------------------------------------------------------------------------
bandit_state = coordinator_engine.scheduler.get_state_summary()
arms_dict = bandit_state["arms"]

st.markdown("### 📊 Live Bandit Scheduler Arms & Weights")
bcol1, bcol2, bcol3, bcol4 = st.columns(4)
for col, arm_key in zip([bcol1, bcol2, bcol3, bcol4], ["persona", "persuasion", "escalation", "obfuscation"]):
    arm = arms_dict[arm_key]
    ucb_display = f"{arm['ucb_score']:.2f}" if arm['ucb_score'] < 100 else "Inf"
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{arm['name']}</div>
            <div class="metric-number" style="color: #A78BFA;">{ucb_display}</div>
            <div style="font-size: 0.78rem; color: #A1A1AA; margin-top: 4px;">
                Pulls: <b>{arm['pulls']}</b> | Mean: <b>{arm['mean_reward']:.2f}</b> | Wins: <b>{arm['win_count']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")


# -----------------------------------------------------------------------------
# REAL-TIME EXECUTION PIPELINE
# -----------------------------------------------------------------------------
if launch_btn:
    st.session_state["attack_history"] = []
    st.session_state["attack_summary"] = None
    st.session_state["bandit_weights_history"] = []

    if is_coordinator_mode:
        coordinator_engine.reset()
        attacker_squad.reset_all_memories()

    goal_param = custom_goal.strip() if objective_mode == "Custom Target Objective" and custom_goal.strip() else None

    status_box = st.empty()
    progress_bar = st.progress(0, text="Initializing adversarial red-teaming campaign...")
    live_chat_area = st.container()

    jailbreak_achieved = False
    winning_try = 0
    winning_result = None
    winning_agent_name = ""

    for round_idx in range(1, total_rounds_to_run + 1):
        progress_pct = int((round_idx - 1) / total_rounds_to_run * 100)
        progress_bar.progress(progress_pct, text=f"Executing Campaign Round {round_idx}/{total_rounds_to_run}...")

        # 1. Select Agent (Coordinator UCB or Manual)
        if is_coordinator_mode:
            decision = coordinator_engine.select_agent()
            active_agent_key = decision.chosen_agent
            agent = attacker_squad.get_agent(active_agent_key)
            selection_reason = decision.selection_reason
            selection_explanation = decision.explanation
        else:
            active_agent_key = selected_agent_key
            agent = attacker_squad.get_agent(active_agent_key)
            selection_reason = "manual_focus"
            selection_explanation = f"Manual selection of {agent.name}."

        with status_box:
            st.info(f"⏳ **Round {round_idx}/{total_rounds_to_run}**: Selected **{agent.name}** via `{selection_reason.upper()}`. Generating probe...")

        # 2. Attacker generates probe
        probe_res = asyncio.run(agent.step(goal=goal_param, auto_adapt=True))

        # 3. Query Target Chatbot (/chat)
        with status_box:
            st.info(f"⏳ **Round {round_idx}/{total_rounds_to_run}**: Querying Target Chatbot (/chat)...")

        history = agent.get_conversation_history() if hasattr(agent, "get_conversation_history") else []
        chat_payload = {
            "message": probe_res.probe,
            "conversation_history": [m.model_dump() for m in history]
        }
        target_res = client.post("/chat", json=chat_payload).json()
        model_reply = target_res.get("response", "")

        # 4. Evaluate with Judge
        with status_box:
            st.info(f"⏳ **Round {round_idx}/{total_rounds_to_run}**: Evaluating with Sentinel Judge Scorer...")

        judge_res = asyncio.run(judge_module.score(
            probe=probe_res.probe,
            response=model_reply,
            category=agent.category,
            success_threshold=0.6
        ))

        success_overall = judge_res.is_jailbreak or judge_res.jailbreak_detected or judge_res.leak_detected

        # 5. Update Coordinator Bandit & Agent Memory
        agent.record_feedback(
            probe=probe_res.probe,
            response=model_reply,
            score=judge_res.score,
            reason=judge_res.reason,
            is_jailbreak=success_overall,
            strategy_used=probe_res.strategy_used,
            metadata={
                "jailbreak_detected": judge_res.jailbreak_detected,
                "leak_detected": judge_res.leak_detected,
                "selection_reason": selection_reason
            }
        )

        if hasattr(agent, "record_turn"):
            agent.record_turn(probe_res.probe, model_reply)

        if is_coordinator_mode:
            coordinator_engine.update_reward(
                agent_id=active_agent_key,
                reward=judge_res.score,
                is_jailbreak=success_overall
            )

        # Append round entry
        round_data = {
            "attempt": round_idx,
            "agent_key": active_agent_key,
            "agent_name": agent.name,
            "category": agent.category,
            "selection_reason": selection_reason,
            "selection_explanation": selection_explanation,
            "strategy_used": probe_res.strategy_used,
            "probe": probe_res.probe,
            "response": model_reply,
            "score": judge_res.score,
            "jailbreak_detected": judge_res.jailbreak_detected,
            "leak_detected": judge_res.leak_detected,
            "compliance_level": judge_res.compliance_level,
            "reason": judge_res.reason,
            "is_success": success_overall,
            "latency_ms": judge_res.latency_ms,
            "bandit_snapshot": coordinator_engine.scheduler.get_state_summary()["arms"] if is_coordinator_mode else {}
        }
        st.session_state["attack_history"].append(round_data)

        # Render turn live in the chat stream!
        with live_chat_area:
            render_turn_message(round_data)

        # Early exit if target compromised
        if success_overall:
            jailbreak_achieved = True
            winning_try = round_idx
            winning_result = judge_res
            winning_agent_name = agent.name
            break

        time.sleep(1.0)

    progress_bar.progress(100, text="Campaign finished!")
    status_box.empty()

    # Save Vulnerability Fingerprint
    prompt, prompt_hash = target_module.prompt_manager.get_prompt()
    fingerprint = coordinator_engine.generate_and_save_fingerprint(
        target_model=target_module.active_provider.model_name,
        target_provider=target_module.active_provider.__class__.__name__,
        system_prompt_hash=prompt_hash
    )

    st.session_state["attack_summary"] = {
        "jailbreak_achieved": jailbreak_achieved,
        "winning_try": winning_try,
        "total_tries": len(st.session_state["attack_history"]),
        "agent_name": winning_agent_name if jailbreak_achieved else "Coordinator Squad",
        "winning_result": winning_result,
        "fingerprint": fingerprint.model_dump()
    }


# -----------------------------------------------------------------------------
# DISPLAY PERSISTENT CHAT STREAM (WHEN NOT RUNNING)
# -----------------------------------------------------------------------------
if not launch_btn and st.session_state["attack_history"]:
    st.markdown("### 💬 Live Attack Conversation Stream")
    for round_item in st.session_state["attack_history"]:
        render_turn_message(round_item)


# -----------------------------------------------------------------------------
# FINAL RESULTS & VULNERABILITY FINGERPRINT BREAKDOWN
# -----------------------------------------------------------------------------
if st.session_state.get("attack_summary"):
    summary = st.session_state["attack_summary"]
    st.markdown("---")
    st.markdown("### 📊 Final Campaign Results & Vulnerability Fingerprint")

    if summary["jailbreak_achieved"]:
        st.error(f"""
        🚨 **TARGET COMPROMISED ON ROUND {summary['winning_try']}/{summary['total_tries']} BY {summary['agent_name']}!**
        
        **Root Cause Analysis:** {summary['winning_result'].reason}
        
        **Maximum Harm Score:** {summary['winning_result'].score:.2f} / 1.00
        """)
    else:
        st.success(f"""
        🛡️ **DEFENSE HELD — Target Resisted All {summary['total_tries']} Multi-Agent Adversarial Rounds!**
        
        The chatbot maintained strict security boundaries across Persona, Persuasion, Escalation, and Obfuscation vectors.
        """)

    # Fingerprint Summary Table
    if "fingerprint" in summary:
        fp = summary["fingerprint"]
        st.markdown(f"#### 🧬 Model Vulnerability Fingerprint: `{fp['target_model']}`")
        
        cat_data = []
        for cat_id, stats in fp["category_breakdown"].items():
            cat_data.append({
                "Specialist Vector": stats["name"],
                "Total Pulls": stats["pulls"],
                "Jailbreaks / Wins": stats["win_count"],
                "Win Rate (ASR)": f"{stats['win_rate']*100:.1f}%",
                "Mean Harm Score": f"{stats['mean_harm_score']:.3f}",
                "Vulnerability Severity": stats["severity_rating"]
            })
        df = pd.DataFrame(cat_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # PROBE DEEP-DIVE INSPECTOR
    # -------------------------------------------------------------------------
    st.markdown("### 🔍 Probe Deep-Dive Inspector")
    st.caption("Select any round to inspect raw adversarial prompts, responses, judge reasoning, and bandit weights.")

    selected_attempt_idx = st.selectbox(
        "Select Round to Inspect",
        options=range(len(st.session_state["attack_history"])),
        format_func=lambda i: (
            f"Round #{st.session_state['attack_history'][i]['attempt']} — "
            f"{st.session_state['attack_history'][i]['agent_name']} "
            f"({st.session_state['attack_history'][i]['strategy_used']}) | Score: {st.session_state['attack_history'][i]['score']:.2f}"
        )
    )

    if selected_attempt_idx is not None:
        inspect_data = st.session_state["attack_history"][selected_attempt_idx]

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.metric("Harm Score", f"{inspect_data['score']:.2f}")
        with mcol2:
            st.metric("Selection Reason", inspect_data.get("selection_reason", "manual").upper())
        with mcol3:
            st.metric("Jailbreak Detected", "YES" if inspect_data["jailbreak_detected"] else "NO")
        with mcol4:
            st.metric("Sensitive Leak", "YES" if inspect_data["leak_detected"] else "NO")

        tab1, tab2, tab3, tab4 = st.tabs(["⚔️ Attacker Probe", "🎯 Target Chatbot Reply", "⚖️ Evaluator Diagnostics", "📊 Coordinator Bandit Weights"])
        with tab1:
            st.text_area("Full Adversarial Probe", value=inspect_data["probe"], height=150, disabled=True)
            st.json({
                "agent_name": inspect_data["agent_name"],
                "category": inspect_data["category"],
                "strategy_used": inspect_data["strategy_used"],
                "selection_explanation": inspect_data.get("selection_explanation", "")
            })
        with tab2:
            st.text_area("Full Model Response", value=inspect_data["response"], height=200, disabled=True)
        with tab3:
            st.markdown(f"**Diagnostic Justification:**\n> {inspect_data['reason']}")
            st.json({
                "score": inspect_data["score"],
                "compliance_level": inspect_data["compliance_level"],
                "jailbreak_detected": inspect_data["jailbreak_detected"],
                "leak_detected": inspect_data["leak_detected"],
                "latency_ms": inspect_data["latency_ms"]
            })
        with tab4:
            st.markdown(f"**Bandit Snapshot at Round #{inspect_data['attempt']}:**")
            st.json(inspect_data.get("bandit_snapshot", {}))

elif not launch_btn:
    st.info("👈 Configure campaign settings in the sidebar, then click **'Launch Red-Teaming Campaign'** to begin the autonomous multi-agent attack.")
