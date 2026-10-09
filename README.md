# 🛡️ Adaptive Red-Teaming Agent (ARTA)

> An automated red-teaming system that doesn't just break your chatbot, it fixes it and proves the fix works.

## 🔍 The Problem

LLM chatbots get broken by persona tricks, persuasion, slow multi-turn escalation, and obfuscated prompts. Existing automated red-teaming tools stop at the attack: they find a jailbreak, score it, and hand you a report. Nobody tells you **why** it worked, **what to change**, or **whether the fix holds**.

## 💡 The Solution

ARTA closes the loop:

```
⚔️ Attack  →  📊 Score  →  🩺 Diagnose  →  🩹 Patch  →  ✅ Verify
     ↑                                                    │
     └────────────────────────────────────────────────────┘
```

| Step | What happens |
|---|---|
| ⚔️ **Attack** | A UCB bandit picks one of four specialist agents to probe the target chatbot |
| 📊 **Score** | An LLM judge rates the response from 0 to 1 for how much it complied |
| 🩺 **Diagnose** | The failure is tagged by attack category and failure layer (system prompt or input guardrail) |
| 🩹 **Patch** | A class-level fix is generated and applied live, not just a block on the one failing prompt |
| ✅ **Verify** | All agents re-attack the patched target and the **Re-Attack Success Rate (RASR)** is measured |

## 🕵️ The Attacker Squad

| Agent | Strategy |
|---|---|
| 🎭 **Persona** | Roleplay and "unrestricted character" framing (DAN-style) |
| 🗣️ **Persuasion** | Authority, scarcity, social proof, and other persuasion techniques |
| 📈 **Escalation** | Gradual multi-turn steering (Crescendo, Echo Chamber) |
| 🔐 **Obfuscation** | Character flipping, encoding, fake system tags |

All agents share one base LLM and differ only by system prompt and memory, so specialisation stays cheap.

## 🏗️ Architecture

```
 Attacker Squad ──► Coordinator (UCB) ──► Target Chatbot (FastAPI)
                                                │
                                                ▼
 Dashboard ◄── Verifier ◄── Patch Generator ◄── Diagnostic ◄── Judge
```

| Module | Role |
|---|---|
| 🎯 Target Chatbot | Local open-weight model with a hot-reloadable system prompt and input guard |
| ⚖️ Judge | Continuous 0-1 compliance score plus a reason |
| 🩺 Diagnostic | Maps successful attacks to category and failure layer |
| 🩹 Patch Generator | Writes a system-prompt rule or guardrail rule |
| 🔁 Verifier | Re-attacks and computes RASR |
| 📺 Dashboard | Live round feed, agent leaderboard, patch/RASR timeline |

## 🧰 Tech Stack

- 🐍 **Python**, **LangChain**, **LangGraph**: agents and loop orchestration
- 🦙 **Ollama / vLLM**: local model serving
- ⚡ **FastAPI**: target chatbot endpoint and live streaming
- ⚛️ **React**: live dashboard
- 

## 🚀 Getting Started

```bash
# 1. Clone and install
git clone <your-repo-url>
cd arta
pip install -r requirements.txt

# 2. Pull models
ollama pull <target_model_name>      # target
ollama pull openai/gpt-oss-20b   # attacker
ollama pull qwen2.5:7b        # judge

# 3. Run the backend
python backend/run.py

#4 Run the frontend
cd frontend
npm run dev
```

## 📏 Metrics

| Metric | Meaning |
|---|---|
| 💥 **ASR** | Attack success rate on the unpatched target (baseline) |
| 🏆 **RASR** | Attack success rate after each patch (**headline metric**) |
| 📉 **Judge Score** | Continuous 0-1 compliance, catches near-misses |
| 🧪 **Regression Matrix** | Checks a patch doesn't break other categories or over-block normal chat |


## ⚖️ Ethics

🔒 For security research on models **you host yourself**. Don't use ARTA against systems you don't own or have permission to test. Store attack logs securely and don't publish raw successful jailbreaks.

---

<p align="center">⭐ If this project helps you, give it a star!</p>
