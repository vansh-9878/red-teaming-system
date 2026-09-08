import React, { useState } from 'react';
import { Search, Swords, Bot, Scale, ShieldAlert, ShieldCheck, ChevronDown } from 'lucide-react';

export default function ProbeInspector({ messages }) {
  const [selectedIdx, setSelectedIdx] = useState(0);

  if (!messages || messages.length === 0) {
    return (
      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#000000',
        color: '#8E8270',
        fontSize: '0.9rem'
      }}>
        No rounds available to inspect. Launch a red-teaming campaign first.
      </div>
    );
  }

  const current = messages[selectedIdx] || messages[0];
  const isJailbreak = current.jailbreak_detected || current.is_success;

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      backgroundColor: '#000000',
      overflowY: 'auto',
      padding: '2rem'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#E1DCC9', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Search size={24} color="#D97706" />
            Probe Deep-Dive Inspector
          </h2>
          <p style={{ fontSize: '0.82rem', color: '#A89E8C', marginTop: '0.25rem' }}>
            Inspect raw inputs, target responses, evaluator JSON reasoning, and bandit weights per round.
          </p>
        </div>

        {/* Round Selector Dropdown */}
        <select
          value={selectedIdx}
          onChange={(e) => setSelectedIdx(parseInt(e.target.value))}
          style={{
            backgroundColor: '#1F150C',
            border: '1px solid #5E4120',
            borderRadius: '8px',
            color: '#E1DCC9',
            padding: '0.6rem 1rem',
            fontSize: '0.85rem',
            outline: 'none',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          {messages.map((m, idx) => (
            <option key={idx} value={idx}>
              Round #{m.round} — {m.agent_name} ({m.strategy_used || m.category}) | Score: {m.score?.toFixed(2)}
            </option>
          ))}
        </select>
      </div>

      {/* KPI Cards for Selected Round */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ backgroundColor: '#1F150C', border: '1px solid #412D15', borderRadius: '10px', padding: '0.9rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.72rem', color: '#A89E8C', textTransform: 'uppercase', fontWeight: 700 }}>Harm Score</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: current.score >= 0.6 ? '#E63946' : '#2A9D8F', marginTop: '0.2rem' }}>
            {current.score?.toFixed(2)} / 1.00
          </div>
        </div>

        <div style={{ backgroundColor: '#1F150C', border: '1px solid #412D15', borderRadius: '10px', padding: '0.9rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.72rem', color: '#A89E8C', textTransform: 'uppercase', fontWeight: 700 }}>Selection Rationale</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#D97706', marginTop: '0.35rem', textTransform: 'uppercase' }}>
            {current.selection_reason || 'MANUAL'}
          </div>
        </div>

        <div style={{ backgroundColor: '#1F150C', border: '1px solid #412D15', borderRadius: '10px', padding: '0.9rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.72rem', color: '#A89E8C', textTransform: 'uppercase', fontWeight: 700 }}>Jailbreak Detected</div>
          <div style={{ fontSize: '1.3rem', fontWeight: 800, color: current.jailbreak_detected ? '#E63946' : '#2A9D8F', marginTop: '0.25rem' }}>
            {current.jailbreak_detected ? 'YES' : 'NO'}
          </div>
        </div>

        <div style={{ backgroundColor: '#1F150C', border: '1px solid #412D15', borderRadius: '10px', padding: '0.9rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.72rem', color: '#A89E8C', textTransform: 'uppercase', fontWeight: 700 }}>Sensitive Leak</div>
          <div style={{ fontSize: '1.3rem', fontWeight: 800, color: current.leak_detected ? '#E63946' : '#2A9D8F', marginTop: '0.25rem' }}>
            {current.leak_detected ? 'YES' : 'NO'}
          </div>
        </div>
      </div>

      {/* Raw Panels */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Attacker Probe */}
        <div style={{ backgroundColor: '#1F150C', border: '1px solid #412D15', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.6rem' }}>
            <Swords size={16} color="#D97706" />
            <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#E1DCC9' }}>

              Raw Attacker Probe ({current.agent_name})
            </h3>
          </div>
          <pre style={{
            backgroundColor: '#140D07',
            border: '1px solid #32210F',
            borderRadius: '8px',
            padding: '1rem',
            color: '#E1DCC9',
            fontSize: '0.84rem',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            fontFamily: 'monospace'
          }}>
            {current.probe}
          </pre>
        </div>

        {/* Target Response */}
        <div style={{ backgroundColor: '#1F150C', border: '1px solid #412D15', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.6rem' }}>
            <Bot size={16} color="#D97706" />
            <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#E1DCC9' }}>
              Raw Target Model Response
            </h3>
          </div>
          <pre style={{
            backgroundColor: '#140D07',
            border: '1px solid #32210F',
            borderRadius: '8px',
            padding: '1rem',
            color: '#E1DCC9',
            fontSize: '0.84rem',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            fontFamily: 'monospace'
          }}>
            {current.response || 'No response recorded.'}
          </pre>
        </div>

        {/* Evaluator Reason */}
        <div style={{ backgroundColor: '#1F150C', border: '1px solid #412D15', borderRadius: '12px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.6rem' }}>
            <Scale size={16} color="#2A9D8F" />
            <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#E1DCC9' }}>
              Sentinel Judge Diagnostic Rationale
            </h3>
          </div>
          <div style={{
            backgroundColor: '#140D07',
            border: '1px solid #32210F',
            borderRadius: '8px',
            padding: '1rem',
            color: '#E1DCC9',
            fontSize: '0.85rem',
            lineHeight: 1.55
          }}>
            {current.reason}
          </div>
        </div>
      </div>
    </div>
  );
}
