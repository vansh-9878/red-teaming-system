import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  Wrench,
  Sparkles,
  RotateCcw,
  FileText,
  ShieldAlert,
  CheckCircle2,
  AlertCircle,
  Layers,
  Code2,
  RefreshCw,
  Hash,
} from "lucide-react";

export default function PatchGeneratorView({ messages, campaignSummary }) {
  const [statusData, setStatusData] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [activeSystemPrompt, setActiveSystemPrompt] = useState("");
  const [activeGuardrails, setActiveGuardrails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  const fetchPatchState = () => {
    // 1. Fetch Patch Engine Status
    fetch("http://localhost:8000/patch/status")
      .then((res) => res.json())
      .then((data) => setStatusData(data))
      .catch(() => {});

    // 2. Fetch Audit Logs
    fetch("http://localhost:8000/patch/audit-log")
      .then((res) => res.json())
      .then((data) => setAuditLogs(data))
      .catch(() => {});

    // 3. Fetch Active System Prompt
    fetch("http://localhost:8000/prompt")
      .then((res) => res.json())
      .then((data) => setActiveSystemPrompt(data.prompt || ""))
      .catch(() => {});

    // 4. Fetch Active Guardrail Rules
    fetch("http://localhost:8000/guardrails")
      .then((res) => res.json())
      .then((data) => setActiveGuardrails(data.input_rules || []))
      .catch(() => {});
  };

  useEffect(() => {
    fetchPatchState();
    const interval = setInterval(fetchPatchState, 3000);
    return () => clearInterval(interval);
  }, []);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 4000);
  };

  // Collect all breach diagnoses from messages / campaignSummary
  const getUnpatchedDiagnoses = () => {
    const diagnoses = [];
    messages.forEach((m) => {
      if (m.diagnosis) {
        diagnoses.push(m.diagnosis);
      } else if (
        m.is_success ||
        m.jailbreak_detected ||
        m.leak_detected ||
        (m.score && m.score >= 0.6)
      ) {
        diagnoses.push({
          category: m.category || "persona",
          layer:
            m.category === "obfuscation" ? "input_guardrail" : "system_prompt",
          evidence: m.reason || "Safety breach detected.",
          triggering_probe: m.probe || "",
          round_index: m.round,
          agent_name: m.agent_name,
          score: m.score,
        });
      }
    });
    return diagnoses;
  };

  const handleApplyAllPatches = async () => {
    const diagnoses = getUnpatchedDiagnoses();
    if (diagnoses.length === 0) {
      showToast(
        "No breach diagnoses available to patch. Run a campaign first!",
      );
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/patch/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ diagnoses, use_llm: true, dry_run: false }),
      });
      const data = await res.json();
      showToast(
        `Applied ${data.total_applied} live patches (${data.system_prompt_patches} prompt, ${data.input_guardrail_patches} guardrails)!`,
      );
      fetchPatchState();
    } catch (e) {
      showToast(`Error applying patches: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRollbackSingle = async (patchId) => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/patch/rollback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patch_id: patchId,
          rollback_to_baseline: false,
        }),
      });
      const data = await res.json();
      showToast(data.message || "Patch rolled back successfully.");
      fetchPatchState();
    } catch (e) {
      showToast(`Error rolling back: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRollbackBaseline = async () => {
    if (
      !window.confirm(
        "Are you sure you want to revert all patches back to the clean baseline?",
      )
    )
      return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/patch/rollback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rollback_to_baseline: true }),
      });
      const data = await res.json();
      showToast(data.message || "Target system reverted to baseline.");
      fetchPatchState();
    } catch (e) {
      showToast(`Error rolling back to baseline: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const breachesCount = getUnpatchedDiagnoses().length;

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        backgroundColor: "#000000",
        overflowY: "auto",
        padding: "2rem",
      }}
    >
      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: "fixed",
            top: "20px",
            right: "20px",
            backgroundColor: "#412D15",
            border: "1px solid #D97706",
            borderRadius: "8px",
            padding: "0.75rem 1.2rem",
            color: "#E1DCC9",
            fontSize: "0.86rem",
            fontWeight: 600,
            boxShadow: "0 8px 24px rgba(0,0,0,0.6)",
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}
        >
          <Sparkles size={16} color="#D97706" />
          {toastMessage}
        </div>
      )}

      {/* Header */}
      <div
        style={{
          marginBottom: "1.5rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          <h2
            style={{
              fontSize: "1.4rem",
              fontWeight: 800,
              color: "#E1DCC9",
              letterSpacing: "-0.02em",
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
            }}
          >
            {/* <Wrench size={24} color="#D97706" /> */}
            Live Patch Generator & Audit Trail
          </h2>
          {/* <p
            style={{
              fontSize: "0.82rem",
              color: "#A89E8C",
              marginTop: "0.25rem",
            }}
          >
            Automated class-level defense synthesis: System-Prompt Constraints &
            Input Guardrails hot-reloaded with zero restarts.
          </p> */}
        </div>

        {/* Action Buttons */}
        <div style={{ display: "flex", gap: "0.75rem" }}>
          {/* <button
            onClick={handleApplyAllPatches}
            disabled={loading || breachesCount === 0}
            style={{
              backgroundColor: breachesCount > 0 ? '#D97706' : '#412D15',
              color: '#E1DCC9',
              border: 'none',
              borderRadius: '8px',
              padding: '0.6rem 1.1rem',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: breachesCount > 0 ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              opacity: breachesCount > 0 ? 1 : 0.6,
              transition: 'all 0.2s ease'
            }}
          >
            <Sparkles size={16} />
            {loading ? 'Synthesizing Patches...' : `Auto-Patch All Breaches (${breachesCount})`}
          </button> */}

          <button
            onClick={handleRollbackBaseline}
            disabled={loading}
            style={{
              backgroundColor: "#1F150C",
              color: "#E63946",
              border: "1px solid #5E4120",
              borderRadius: "8px",
              padding: "0.6rem 1rem",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.45rem",
            }}
          >
            <RotateCcw size={15} />
            Rollback to Baseline
          </button>
        </div>
      </div>

      {/* Telemetry KPI Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "1rem",
          marginBottom: "1.5rem",
        }}
      >
        <div
          style={{
            backgroundColor: "#1F150C",
            border: "1px solid #412D15",
            borderRadius: "10px",
            padding: "0.9rem",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "0.72rem",
              color: "#A89E8C",
              textTransform: "uppercase",
              fontWeight: 700,
            }}
          >
            Total Patches Applied
          </div>
          <div
            style={{
              fontSize: "1.6rem",
              fontWeight: 800,
              color: "#D97706",
              marginTop: "0.2rem",
            }}
          >
            {statusData?.total_patches_applied ?? auditLogs.length}
          </div>
        </div>

        <div
          style={{
            backgroundColor: "#1F150C",
            border: "1px solid #412D15",
            borderRadius: "10px",
            padding: "0.9rem",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "0.72rem",
              color: "#A89E8C",
              textTransform: "uppercase",
              fontWeight: 700,
            }}
          >
            System Prompt Hash
          </div>
          <div
            style={{
              fontSize: "1.1rem",
              fontWeight: 700,
              color: "#2A9D8F",
              marginTop: "0.35rem",
              fontFamily: "monospace",
            }}
          >
            {statusData?.system_prompt_hash || "baseline"}
          </div>
        </div>

        <div
          style={{
            backgroundColor: "#1F150C",
            border: "1px solid #412D15",
            borderRadius: "10px",
            padding: "0.9rem",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "0.72rem",
              color: "#A89E8C",
              textTransform: "uppercase",
              fontWeight: 700,
            }}
          >
            Active Input Guardrails
          </div>
          <div
            style={{
              fontSize: "1.6rem",
              fontWeight: 800,
              color: "#E1DCC9",
              marginTop: "0.2rem",
            }}
          >
            {statusData?.input_guardrails_count ?? activeGuardrails.length}
          </div>
        </div>

        <div
          style={{
            backgroundColor: "#1F150C",
            border: "1px solid #412D15",
            borderRadius: "10px",
            padding: "0.9rem",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "0.72rem",
              color: "#A89E8C",
              textTransform: "uppercase",
              fontWeight: 700,
            }}
          >
            Live Hot-Reload
          </div>
          <div
            style={{
              fontSize: "1.1rem",
              fontWeight: 700,
              color: "#2A9D8F",
              marginTop: "0.35rem",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.3rem",
            }}
          >
            <CheckCircle2 size={16} /> ACTIVE
          </div>
        </div>
      </div>

      {/* Main Grid: Audit Log & Live Code Inspect */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1.2fr 1fr",
          gap: "1.25rem",
          flex: 1,
        }}
      >
        {/* Left: Audit Trail Table (Module 9) */}
        <div
          style={{
            backgroundColor: "#1F150C",
            border: "1px solid #412D15",
            borderRadius: "12px",
            padding: "1.25rem",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "0.9rem",
            }}
          >
            <h3
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                color: "#E1DCC9",
                display: "flex",
                alignItems: "center",
                gap: "0.45rem",
              }}
            >
              <Layers size={17} color="#D97706" />
              Patch Audit Trail ({auditLogs.length} Records)
            </h3>
            <button
              onClick={fetchPatchState}
              style={{
                background: "none",
                border: "none",
                color: "#A89E8C",
                cursor: "pointer",
              }}
              title="Refresh"
            >
              <RefreshCw size={14} />
            </button>
          </div>

          <div style={{ flex: 1, overflowY: "auto", maxHeight: "520px" }}>
            {auditLogs.length === 0 ? (
              <div
                style={{
                  color: "#8E8270",
                  fontSize: "0.84rem",
                  padding: "2rem 1rem",
                  textAlign: "center",
                }}
              >
                No patches generated yet.
              </div>
            ) : (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.65rem",
                }}
              >
                {auditLogs
                  .slice()
                  .reverse()
                  .map((p, idx) => (
                    <div
                      key={p.patch_id || idx}
                      style={{
                        backgroundColor: "#140D07",
                        border: "1px solid #32210F",
                        borderRadius: "8px",
                        padding: "0.85rem",
                        fontSize: "0.82rem",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          marginBottom: "0.35rem",
                        }}
                      >
                        <span
                          style={{
                            fontWeight: 700,
                            color:
                              p.target_layer === "system_prompt"
                                ? "#2A9D8F"
                                : "#D97706",
                            textTransform: "uppercase",
                            fontSize: "0.74rem",
                          }}
                        >
                          [{p.target_layer}] {p.patch_type}
                        </span>
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "0.35rem",
                          }}
                        >
                          {p.synthesized_by && (
                            <span
                              style={{
                                fontSize: "0.66rem",
                                padding: "1px 5px",
                                borderRadius: "3px",
                                backgroundColor: "#2A9D8F22",
                                color: "#6EE7B7",
                                border: "1px solid #2A9D8F44",
                                fontFamily: "monospace",
                              }}
                            >
                              {p.synthesized_by}
                            </span>
                          )}
                          <span
                            style={{
                              fontSize: "0.68rem",
                              padding: "2px 6px",
                              borderRadius: "4px",
                              backgroundColor:
                                p.status === "applied"
                                  ? "#2A9D8F22"
                                  : "#E6394622",
                              color:
                                p.status === "applied" ? "#2A9D8F" : "#E63946",
                              fontWeight: 700,
                            }}
                          >
                            {p.status}
                          </span>
                        </div>
                      </div>

                      <div
                        style={{
                          color: "#A89E8C",
                          fontSize: "0.78rem",
                          marginBottom: "0.4rem",
                        }}
                      >
                        <strong>Trigger:</strong>{" "}
                        {p.triggering_diagnosis?.category || "Unknown"} (Round #
                        {p.triggering_diagnosis?.round_index || "N/A"})
                        {p.explanation && (
                          <span
                            style={{
                              display: "block",
                              color: "#8E8270",
                              fontSize: "0.72rem",
                              marginTop: "2px",
                            }}
                          >
                            💡 {p.explanation}
                          </span>
                        )}
                      </div>

                      <pre
                        style={{
                          backgroundColor: "#0A0603",
                          border: "1px solid #24170B",
                          borderRadius: "4px",
                          padding: "0.5rem",
                          color: "#E1DCC9",
                          fontSize: "0.74rem",
                          whiteSpace: "pre-wrap",
                          wordBreak: "break-word",
                          maxHeight: "80px",
                          overflowY: "auto",
                        }}
                      >
                        {p.patch_content}
                      </pre>

                      {p.status === "applied" && (
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "flex-end",
                            marginTop: "0.45rem",
                          }}
                        >
                          <button
                            onClick={() => handleRollbackSingle(p.patch_id)}
                            style={{
                              backgroundColor: "transparent",
                              border: "1px solid #5E4120",
                              borderRadius: "4px",
                              color: "#E63946",
                              fontSize: "0.72rem",
                              padding: "2px 8px",
                              cursor: "pointer",
                            }}
                          >
                            Revert Patch
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Live Patched Files Inspection */}
        <div
          style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}
        >
          {/* Live System Prompt */}
          <div
            style={{
              backgroundColor: "#1F150C",
              border: "1px solid #412D15",
              borderRadius: "12px",
              padding: "1.25rem",
              flex: 1,
              display: "flex",
              flexDirection: "column",
            }}
          >
            <h3
              style={{
                fontSize: "0.92rem",
                fontWeight: 700,
                color: "#E1DCC9",
                marginBottom: "0.6rem",
                display: "flex",
                alignItems: "center",
                gap: "0.4rem",
              }}
            >
              <FileText size={16} color="#2A9D8F" />
              Live Target System Prompt (system_prompt.txt)
            </h3>
            <pre
              style={{
                flex: 1,
                backgroundColor: "#140D07",
                border: "1px solid #32210F",
                borderRadius: "8px",
                padding: "0.85rem",
                color: "#E1DCC9",
                fontSize: "0.78rem",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                overflowY: "auto",
                maxHeight: "220px",
                fontFamily: "monospace",
              }}
            >
              {activeSystemPrompt}
            </pre>
          </div>

          {/* Live Input Guardrails Config */}
          <div
            style={{
              backgroundColor: "#1F150C",
              border: "1px solid #412D15",
              borderRadius: "12px",
              padding: "1.25rem",
              flex: 1,
              display: "flex",
              flexDirection: "column",
            }}
          >
            <h3
              style={{
                fontSize: "0.92rem",
                fontWeight: 700,
                color: "#E1DCC9",
                marginBottom: "0.6rem",
                display: "flex",
                alignItems: "center",
                gap: "0.4rem",
              }}
            >
              <Code2 size={16} color="#D97706" />
              Live Input Guardrail Rules (guardrails.json)
            </h3>
            <pre
              style={{
                flex: 1,
                backgroundColor: "#140D07",
                border: "1px solid #32210F",
                borderRadius: "8px",
                padding: "0.85rem",
                color: "#E1DCC9",
                fontSize: "0.76rem",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                overflowY: "auto",
                maxHeight: "220px",
                fontFamily: "monospace",
              }}
            >
              {JSON.stringify(activeGuardrails, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
