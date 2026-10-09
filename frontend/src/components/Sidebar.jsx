import React from "react";
import {
  ShieldAlert,
  Play,
  Square,
  RotateCcw,
  Bot,
  Cpu,
  Scale,
  Compass,
  Target,
  Flame,
  BarChart3,
  Search,
  MessageSquare,
  Wrench,
  ShieldCheck,
  Settings,
} from "lucide-react";

export default function Sidebar({
  activeTab,
  setActiveTab,
  mode,
  setMode,
  enablePatching,
  setEnablePatching,
  selectedAgent,
  setSelectedAgent,
  totalRounds,
  setTotalRounds,
  objectiveMode,
  setObjectiveMode,
  customGoal,
  setCustomGoal,
  isRunning,
  onStartCampaign,
  onStopCampaign,
  onReset,
  modelsInfo,
  onOpenModelConfig,
}) {
  const agentsList = [
    {
      id: "persona",
      name: "🎭 Persona / Roleplay Specialist",
      desc: "Screenplays, DAN, fictional framing",
    },
    {
      id: "persuasion",
      name: "🧠 Persuasion Specialist",
      desc: "ISO audits, crisis deadlines, authority",
    },
    {
      id: "escalation",
      name: "📈 Escalation (Crescendo)",
      desc: "Multi-turn 3-step conversational steering",
    },
    {
      id: "obfuscation",
      name: "🔏 Obfuscation Specialist",
      desc: "Base64, ROT13, 1337speak, delimiters",
    },
  ];

  return (
    <aside
      style={{
        width: "320px",
        minWidth: "320px",
        backgroundColor: "#1F150C",
        borderRight: "1px solid #412D15",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflowY: "auto",
      }}
    >
      {/* Header */}
      <div style={{ padding: "1.25rem", borderBottom: "1px solid #412D15" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.65rem" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              backgroundColor: "#412D15",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "1px solid #553B1C",
            }}
          >
            <ShieldAlert size={20} color="#E1DCC9" />
          </div>
          <div>
            <p
              style={{ fontSize: "0.92rem", color: "#A89E8C", fontWeight: 500 }}
            >
              Adaptive Red-Teaming System
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div
        style={{ padding: "0.75rem 0.6rem", borderBottom: "1px solid #412D15" }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(5, 1fr)",
            gap: "0.25rem",
            backgroundColor: "#140D07",
            padding: "4px",
            borderRadius: "8px",
            border: "1px solid #32210F",
          }}
        >
          <button
            onClick={() => setActiveTab("chat")}
            style={{
              padding: "0.45rem 0.2rem",
              fontSize: "0.74rem",
              fontWeight: 600,
              borderRadius: "6px",
              border: "none",
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.2rem",
              backgroundColor: activeTab === "chat" ? "#412D15" : "transparent",
              color: activeTab === "chat" ? "#E1DCC9" : "#8E8270",
              transition: "all 0.15s ease",
            }}
          >
            <MessageSquare size={13} />
            Chat
          </button>
          <button
            onClick={() => setActiveTab("analytics")}
            style={{
              padding: "0.45rem 0.2rem",
              fontSize: "0.74rem",
              fontWeight: 600,
              borderRadius: "6px",
              border: "none",
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.2rem",
              backgroundColor:
                activeTab === "analytics" ? "#412D15" : "transparent",
              color: activeTab === "analytics" ? "#E1DCC9" : "#8E8270",
              transition: "all 0.15s ease",
            }}
          >
            <BarChart3 size={13} />
            Metrics
          </button>
          <button
            onClick={() => setActiveTab("inspector")}
            style={{
              padding: "0.45rem 0.2rem",
              fontSize: "0.74rem",
              fontWeight: 600,
              borderRadius: "6px",
              border: "none",
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.2rem",
              backgroundColor:
                activeTab === "inspector" ? "#412D15" : "transparent",
              color: activeTab === "inspector" ? "#E1DCC9" : "#8E8270",
              transition: "all 0.15s ease",
            }}
          >
            <Search size={13} />
            Inspect
          </button>
          <button
            onClick={() => setActiveTab("patcher")}
            style={{
              padding: "0.45rem 0.2rem",
              fontSize: "0.74rem",
              fontWeight: 600,
              borderRadius: "6px",
              border: "none",
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.2rem",
              backgroundColor:
                activeTab === "patcher" ? "#412D15" : "transparent",
              color: activeTab === "patcher" ? "#E1DCC9" : "#8E8270",
              transition: "all 0.15s ease",
            }}
          >
            <Wrench size={13} />
            Patches
          </button>
          <button
            onClick={() => setActiveTab("verifier")}
            style={{
              padding: "0.45rem 0.2rem",
              fontSize: "0.74rem",
              fontWeight: 600,
              borderRadius: "6px",
              border: "none",
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.2rem",
              backgroundColor:
                activeTab === "verifier" ? "#412D15" : "transparent",
              color: activeTab === "verifier" ? "#34D399" : "#8E8270",
              transition: "all 0.15s ease",
            }}
          >
            <ShieldCheck size={13} />
            RASR
          </button>
        </div>
      </div>

      {/* Active Models Info Box */}
      <div style={{ padding: "1rem", borderBottom: "1px solid #412D15" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "0.5rem",
          }}
        >
          <span
            style={{
              fontSize: "0.72rem",
              fontWeight: 700,
              color: "#A89E8C",
              textTransform: "uppercase",
              letterSpacing: "0.04em",
            }}
          >
            Active Model Substrates
          </span>
          {/* <button
            onClick={onOpenModelConfig}
            title="Configure Models & API Keys"
            style={{
              background: "none",
              border: "none",
              color: "#D97706",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.25rem",
              fontSize: "0.7rem",
              fontWeight: 600,
              padding: "2px 4px",
              borderRadius: "4px",
            }}
          >
            <Settings size={12} />
            Edit
          </button> */}
        </div>
        <div
          style={{
            backgroundColor: "#140D07",
            border: "1px solid #32210F",
            borderRadius: "8px",
            padding: "0.75rem",
            fontSize: "0.78rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.4rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <Target size={13} color="#D97706" />
            <span style={{ color: "#8E8270" }}>Target:</span>
            <span
              style={{
                color: "#E1DCC9",
                fontWeight: 600,
                fontFamily: "monospace",
                fontSize: "0.73rem",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {modelsInfo.target}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <Cpu size={13} color="#D97706" />
            <span style={{ color: "#8E8270" }}>Attacker:</span>
            <span
              style={{
                color: "#E1DCC9",
                fontWeight: 600,
                fontFamily: "monospace",
                fontSize: "0.73rem",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {modelsInfo.attacker}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <Scale size={13} color="#D97706" />
            <span style={{ color: "#8E8270" }}>Judge:</span>
            <span
              style={{
                color: "#E1DCC9",
                fontWeight: 600,
                fontFamily: "monospace",
                fontSize: "0.73rem",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {modelsInfo.judge}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <Wrench size={13} color="#2A9D8F" />
            <span style={{ color: "#8E8270" }}>Patcher:</span>
            <span
              style={{
                color: "#E1DCC9",
                fontWeight: 600,
                fontFamily: "monospace",
                fontSize: "0.73rem",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {modelsInfo.patcher || "qwen/qwen3.6-27b (GROQ)"}
            </span>
          </div>
        </div>
      </div>

      {/* Controls Body */}
      <div
        style={{
          padding: "1rem",
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: "1.25rem",
        }}
      >
        {/* Defense & Verification Pipeline Mode */}
        <div>
          <label
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              color: "#A89E8C",
              textTransform: "uppercase",
              display: "block",
              marginBottom: "0.45rem",
            }}
          >
            Remediation & Verification
          </label>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "0.4rem",
            }}
          >
            <button
              onClick={() => setEnablePatching(true)}
              disabled={isRunning}
              style={{
                textAlign: "left",
                padding: "0.6rem 0.65rem",
                backgroundColor: enablePatching ? "#1D2F28" : "#140D07",
                border: `1px solid ${enablePatching ? "#2A9D8F" : "#32210F"}`,
                borderRadius: "8px",
                color: "#E1DCC9",
                cursor: isRunning ? "not-allowed" : "pointer",
                transition: "all 0.15s ease",
              }}
            >
              <div
                style={{
                  fontSize: "0.78rem",
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  gap: "0.35rem",
                  color: enablePatching ? "#34D399" : "#E1DCC9",
                }}
              >
                <ShieldCheck
                  size={14}
                  color={enablePatching ? "#34D399" : "#8E8270"}
                />
                With Patch & RASR
              </div>
              {/* <div
                style={{
                  fontSize: "0.67rem",
                  color: "#8E8270",
                  marginTop: "3px",
                  lineHeight: 1.3,
                }}
              >
                Live auto-patching & verifier replay
              </div> */}
            </button>

            <button
              onClick={() => setEnablePatching(false)}
              disabled={isRunning}
              style={{
                textAlign: "left",
                padding: "0.6rem 0.65rem",
                backgroundColor: !enablePatching ? "#3A1B1C" : "#140D07",
                border: `1px solid ${!enablePatching ? "#E63946" : "#32210F"}`,
                borderRadius: "8px",
                color: "#E1DCC9",
                cursor: isRunning ? "not-allowed" : "pointer",
                transition: "all 0.15s ease",
              }}
            >
              <div
                style={{
                  fontSize: "0.78rem",
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  gap: "0.35rem",
                  color: !enablePatching ? "#FFA5AB" : "#E1DCC9",
                }}
              >
                <ShieldAlert
                  size={14}
                  color={!enablePatching ? "#E63946" : "#8E8270"}
                />
                Attack-Only
              </div>
              {/* <div
                style={{
                  fontSize: "0.67rem",
                  color: "#8E8270",
                  marginTop: "3px",
                  lineHeight: 1.3,
                }}
              >
                Breach detection only (no fixes)
              </div> */}
            </button>
          </div>
        </div>

        {/* Campaign Mode Selection */}
        <div>
          <label
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              color: "#A89E8C",
              textTransform: "uppercase",
              display: "block",
              marginBottom: "0.45rem",
            }}
          >
            Campaign Mode
          </label>
          <div
            style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}
          >
            <button
              onClick={() => setMode("coordinator")}
              disabled={isRunning}
              style={{
                textAlign: "left",
                padding: "0.65rem 0.75rem",
                backgroundColor: mode === "coordinator" ? "#2F2010" : "#140D07",
                border: `1px solid ${mode === "coordinator" ? "#5E4120" : "#32210F"}`,
                borderRadius: "8px",
                color: "#E1DCC9",
                cursor: isRunning ? "not-allowed" : "pointer",
              }}
            >
              <div
                style={{
                  fontSize: "0.82rem",
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  gap: "0.35rem",
                }}
              >
                <Compass size={14} color="#D97706" />
                Autonomous Coordinator (UCB)
              </div>
              <div
                style={{
                  fontSize: "0.7rem",
                  color: "#8E8270",
                  marginTop: "2px",
                }}
              >
                Bandit schedules agents & novelty rule
              </div>
            </button>

            <button
              onClick={() => setMode("single")}
              disabled={isRunning}
              style={{
                textAlign: "left",
                padding: "0.65rem 0.75rem",
                backgroundColor: mode === "single" ? "#2F2010" : "#140D07",
                border: `1px solid ${mode === "single" ? "#5E4120" : "#32210F"}`,
                borderRadius: "8px",
                color: "#E1DCC9",
                cursor: isRunning ? "not-allowed" : "pointer",
              }}
            >
              <div
                style={{
                  fontSize: "0.82rem",
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  gap: "0.35rem",
                }}
              >
                <Flame size={14} color="#E63946" />
                Single Specialist Focus
              </div>
              <div
                style={{
                  fontSize: "0.7rem",
                  color: "#8E8270",
                  marginTop: "2px",
                }}
              >
                Test with 1 dedicated agent squad
              </div>
            </button>
          </div>
        </div>

        {/* If Single Specialist selected */}
        {mode === "single" && (
          <div>
            <label
              style={{
                fontSize: "0.75rem",
                fontWeight: 700,
                color: "#A89E8C",
                textTransform: "uppercase",
                display: "block",
                marginBottom: "0.45rem",
              }}
            >
              Choose Specialist Agent
            </label>
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              disabled={isRunning}
              style={{
                width: "100%",
                backgroundColor: "#140D07",
                border: "1px solid #412D15",
                borderRadius: "8px",
                color: "#E1DCC9",
                padding: "0.55rem",
                fontSize: "0.8rem",
                outline: "none",
              }}
            >
              {agentsList.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Number of Rounds Slider */}
        <div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "0.35rem",
            }}
          >
            <label
              style={{
                fontSize: "0.75rem",
                fontWeight: 700,
                color: "#A89E8C",
                textTransform: "uppercase",
              }}
            >
              Total Rounds
            </label>
            <span
              style={{
                fontSize: "0.82rem",
                fontWeight: 800,
                color: "#E1DCC9",
                fontFamily: "monospace",
              }}
            >
              {totalRounds}
            </span>
          </div>
          <input
            type="range"
            min="3"
            max="40"
            value={totalRounds}
            onChange={(e) => setTotalRounds(parseInt(e.target.value))}
            disabled={isRunning}
            style={{
              width: "100%",
              accentColor: "#D97706",
              cursor: isRunning ? "not-allowed" : "pointer",
            }}
          />
        </div>

        {/* Objective Mode */}
        <div>
          <label
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              color: "#A89E8C",
              textTransform: "uppercase",
              display: "block",
              marginBottom: "0.45rem",
            }}
          >
            Adversarial Objective
          </label>
          <div
            style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}
          >
            <button
              onClick={() => setObjectiveMode("autonomous")}
              disabled={isRunning}
              style={{
                flex: 1,
                padding: "0.4rem",
                fontSize: "0.75rem",
                fontWeight: 600,
                backgroundColor:
                  objectiveMode === "autonomous" ? "#412D15" : "#140D07",
                border: `1px solid ${objectiveMode === "autonomous" ? "#5E4120" : "#32210F"}`,
                borderRadius: "6px",
                color: "#E1DCC9",
                cursor: isRunning ? "not-allowed" : "pointer",
              }}
            >
              Autonomous
            </button>
            <button
              onClick={() => setObjectiveMode("custom")}
              disabled={isRunning}
              style={{
                flex: 1,
                padding: "0.4rem",
                fontSize: "0.75rem",
                fontWeight: 600,
                backgroundColor:
                  objectiveMode === "custom" ? "#412D15" : "#140D07",
                border: `1px solid ${objectiveMode === "custom" ? "#5E4120" : "#32210F"}`,
                borderRadius: "6px",
                color: "#E1DCC9",
                cursor: isRunning ? "not-allowed" : "pointer",
              }}
            >
              Custom Goal
            </button>
          </div>

          {objectiveMode === "custom" && (
            <textarea
              value={customGoal}
              onChange={(e) => setCustomGoal(e.target.value)}
              disabled={isRunning}
              placeholder="e.g. reveal system prompt instructions and internal security rules"
              rows={3}
              style={{
                width: "100%",
                backgroundColor: "#140D07",
                border: "1px solid #412D15",
                borderRadius: "8px",
                color: "#E1DCC9",
                padding: "0.5rem",
                fontSize: "0.78rem",
                outline: "none",
                resize: "none",
              }}
            />
          )}
        </div>
      </div>

      {/* Footer Controls */}
      <div
        style={{
          padding: "1rem",
          borderTop: "1px solid #412D15",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
        }}
      >
        {!isRunning ? (
          <button
            onClick={onStartCampaign}
            className="btn-primary"
            style={{ width: "100%", justifyContent: "center" }}
          >
            <Play size={16} />
            Launch Red-Teaming
          </button>
        ) : (
          <button
            onClick={onStopCampaign}
            className="btn-danger"
            style={{
              width: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.5rem",
            }}
          >
            <Square size={16} />
            Stop Campaign
          </button>
        )}

        <button
          onClick={onReset}
          disabled={isRunning}
          style={{
            width: "100%",
            backgroundColor: "transparent",
            color: "#A89E8C",
            border: "1px solid #32210F",
            borderRadius: "8px",
            padding: "0.5rem",
            fontSize: "0.78rem",
            cursor: isRunning ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "0.4rem",
          }}
        >
          <RotateCcw size={13} />
          Reset State & Memory
        </button>
      </div>
    </aside>
  );
}
