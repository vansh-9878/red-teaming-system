import React, { useRef, useEffect, useState } from 'react';
import { 
  Bot, 
  Swords, 
  Sparkles, 
  ShieldCheck, 
  ShieldAlert, 
  Scale, 
  AlertTriangle, 
  Info,
  ChevronRight,
  Dice5
} from 'lucide-react';

export default function ChatInterface({
  messages,
  currentStatus,
  targetModel
}) {
  const scrollEndRef = useRef(null);
  const [hoveredRound, setHoveredRound] = useState(null);

  useEffect(() => {
    scrollEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStatus]);

  const getAgentColor = () => {
    return '#D97706';
  };


  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      backgroundColor: '#000000',
      position: 'relative'
    }}>
      {/* Chat Header */}
      <header style={{
        padding: '1rem 1.75rem',
        backgroundColor: '#1F150C',
        borderBottom: '1px solid #412D15',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#E1DCC9' }}>
            Live Adversarial Red-Teaming Stream
          </h2>
          <p style={{ fontSize: '0.75rem', color: '#A89E8C' }}>
            Attacker Probes on the Left ⚔️ &bull; Target Chatbot on the Right 🎯 &bull; Hover turns for Evaluator Stats
          </p>
        </div>

        {/* Live Status Pill */}
        {currentStatus ? (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            backgroundColor: '#140D07',
            border: '1px solid #553B1C',
            padding: '0.4rem 0.8rem',
            borderRadius: '9999px',
            fontSize: '0.78rem',
            color: '#E1DCC9'
          }}>
            <span className="typing-dot" style={{ backgroundColor: '#D97706' }}></span>
            <span>{currentStatus}</span>
          </div>
        ) : (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            backgroundColor: '#140D07',
            border: '1px solid #32210F',
            padding: '0.35rem 0.75rem',
            borderRadius: '9999px',
            fontSize: '0.75rem',
            color: '#8E8270'
          }}>
            <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#2A9D8F' }}></span>
            <span>Engine Ready</span>
          </div>
        )}
      </header>

      {/* Messages Scroll Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1.5rem 2rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '2rem'
      }}>
        {messages.length === 0 && !currentStatus && (
          <div style={{
            margin: 'auto',
            textAlign: 'center',
            maxWidth: '460px',
            padding: '2.5rem',
            backgroundColor: '#1F150C',
            border: '1px solid #412D15',
            borderRadius: '16px'
          }}>
            <div style={{
              width: '54px',
              height: '54px',
              borderRadius: '12px',
              backgroundColor: '#140D07',
              border: '1px solid #553B1C',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.25rem'
            }}>
              <Swords size={28} color="#D97706" />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#E1DCC9', marginBottom: '0.5rem' }}>
              Autonomous Red-Teaming Console
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#A89E8C', lineHeight: 1.6 }}>
              Configure your campaign in the sidebar and launch the multi-agent squad to start probing the target chatbot in real-time.
            </p>
          </div>
        )}

        {/* Conversation Turns */}
        {messages.map((turn, index) => {
          const isJailbroken = turn.jailbreak_detected || turn.is_success;
          const isLeaked = turn.leak_detected;
          const agentColor = getAgentColor(turn.category);
          const isHovered = hoveredRound === turn.round;

          return (
            <div 
              key={index}
              onMouseEnter={() => setHoveredRound(turn.round)}
              onMouseLeave={() => setHoveredRound(null)}
              style={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.85rem',
                padding: '1rem 1.25rem',
                backgroundColor: isHovered ? '#1A1109' : 'transparent',
                borderRadius: '14px',
                border: `1px solid ${isHovered ? '#553B1C' : 'transparent'}`,
                transition: 'all 0.2s ease'
              }}
            >
              {/* Turn Header */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '0.4rem',
                borderBottom: '1px solid #281A0E'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#E1DCC9', fontFamily: 'monospace' }}>
                    ROUND #{turn.round}
                  </span>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    padding: '0.15rem 0.5rem',
                    borderRadius: '4px',
                    backgroundColor: 'rgba(65, 45, 21, 0.4)',
                    color: agentColor,
                    border: `1px solid ${agentColor}40`
                  }}>
                    {turn.agent_name}
                  </span>
                  {turn.selection_reason && (
                    <span style={{ fontSize: '0.7rem', color: '#8E8270', fontFamily: 'monospace' }}>
                      ({turn.selection_reason})
                    </span>
                  )}
                </div>

                {/* Hover indicator pill */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.72rem', color: '#8E8270' }}>
                  <Info size={12} color="#8E8270" />
                  <span>Hover for Evaluator Stats</span>
                </div>
              </div>

              {/* 1. Left Message: Attacker Probe */}
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  maxWidth: '78%',
                  backgroundColor: '#1F150C',
                  border: `1px solid ${agentColor}60`,
                  borderRadius: '14px 14px 14px 2px',
                  padding: '1rem 1.2rem',
                  color: '#E1DCC9',
                  boxShadow: '0 4px 14px rgba(0,0,0,0.5)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.45rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Swords size={14} color={agentColor} />
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: agentColor }}>
                        {turn.agent_name} (Attacker)
                      </span>
                    </div>
                    <span style={{ fontSize: '0.68rem', color: '#8E8270', fontFamily: 'monospace' }}>
                      {turn.strategy_used || turn.category}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.88rem', lineHeight: 1.55, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {turn.probe}
                  </div>
                </div>
              </div>

              {/* 2. Right Message: Target Chatbot Response (Rendered if available) */}
              {turn.response ? (
                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <div style={{
                    maxWidth: '78%',
                    backgroundColor: '#140D07',
                    border: '1px solid #412D15',
                    borderRadius: '14px 14px 2px 14px',
                    padding: '1rem 1.2rem',
                    color: '#E1DCC9',
                    boxShadow: '0 4px 14px rgba(0,0,0,0.5)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.45rem' }}>
                      <span style={{ fontSize: '0.68rem', color: '#8E8270', fontFamily: 'monospace' }}>
                        {targetModel || 'Target Chatbot'}
                      </span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#D97706' }}>
                          Target Chatbot
                        </span>
                        <Bot size={14} color="#D97706" />
                      </div>
                    </div>
                    <div style={{ fontSize: '0.88rem', lineHeight: 1.55, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                      {turn.response}
                    </div>
                  </div>
                </div>
              ) : (
                /* Target Thinking Indicator inside turn */
                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <div style={{
                    backgroundColor: '#140D07',
                    border: '1px solid #32210F',
                    borderRadius: '12px',
                    padding: '0.65rem 1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    color: '#A89E8C',
                    fontSize: '0.78rem'
                  }}>
                    <span className="typing-dot" style={{ backgroundColor: '#D97706' }}></span>
                    <span className="typing-dot" style={{ backgroundColor: '#D97706' }}></span>
                    <span className="typing-dot" style={{ backgroundColor: '#D97706' }}></span>
                    <span style={{ marginLeft: '4px' }}>Target chatbot is responding...</span>
                  </div>
                </div>
              )}

              {/* 3. FLOATING STATS POPOVER ON HOVER */}
              {isHovered && turn.score !== undefined && (
                <div style={{
                  position: 'absolute',
                  top: '10px',
                  right: '15px',
                  width: '340px',
                  backgroundColor: '#140D07',
                  border: '1px solid #5E4120',
                  borderRadius: '12px',
                  padding: '0.9rem 1rem',
                  boxShadow: '0 12px 35px rgba(0, 0, 0, 0.9), 0 0 1px 1px rgba(225, 220, 201, 0.1)',
                  zIndex: 40,
                  animation: 'fadeIn 0.15s ease'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <Scale size={14} color="#D97706" />
                      <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#E1DCC9' }}>
                        Sentinel Evaluator Stats
                      </span>
                    </div>
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      padding: '0.1rem 0.45rem',
                      borderRadius: '4px',
                      backgroundColor: isJailbroken ? 'rgba(230,57,70,0.2)' : 'rgba(42,157,143,0.2)',
                      color: isJailbroken ? '#FFA5AB' : '#6EE7B7',
                      border: `1px solid ${isJailbroken ? '#E63946' : '#2A9D8F'}`
                    }}>
                      {isJailbroken ? 'JAILBREAK' : 'DEFENSE HELD'}
                    </span>
                  </div>

                  {/* Harm Score Progress Meter */}
                  <div style={{ marginBottom: '0.6rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: '0.2rem' }}>
                      <span style={{ color: '#8E8270' }}>Harm Score:</span>
                      <span style={{ fontWeight: 800, color: turn.score >= 0.6 ? '#E63946' : '#2A9D8F' }}>
                        {turn.score?.toFixed(2)} / 1.00 ({turn.compliance_level || 'evaluated'})
                      </span>
                    </div>
                    <div style={{ height: '6px', backgroundColor: '#281A0E', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{
                        height: '100%',
                        width: `${Math.round((turn.score || 0) * 100)}%`,
                        backgroundColor: turn.score >= 0.6 ? '#E63946' : '#2A9D8F'
                      }} />
                    </div>
                  </div>

                  {/* Badges Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem', marginBottom: '0.6rem' }}>
                    <div style={{ backgroundColor: '#1F150C', padding: '0.35rem 0.5rem', borderRadius: '6px', fontSize: '0.7rem' }}>
                      <span style={{ color: '#8E8270' }}>Jailbreak: </span>
                      <b style={{ color: turn.jailbreak_detected ? '#E63946' : '#2A9D8F' }}>
                        {turn.jailbreak_detected ? 'YES' : 'NO'}
                      </b>
                    </div>
                    <div style={{ backgroundColor: '#1F150C', padding: '0.35rem 0.5rem', borderRadius: '6px', fontSize: '0.7rem' }}>
                      <span style={{ color: '#8E8270' }}>Sensitive Leak: </span>
                      <b style={{ color: turn.leak_detected ? '#E63946' : '#2A9D8F' }}>
                        {turn.leak_detected ? 'YES' : 'NO'}
                      </b>
                    </div>
                  </div>

                  {/* Diagnostic Reason */}
                  {turn.reason && (
                    <div style={{ fontSize: '0.74rem', color: '#C5BCAB', lineHeight: 1.45, backgroundColor: '#1F150C', padding: '0.5rem', borderRadius: '6px', border: '1px solid #32210F' }}>
                      <b style={{ color: '#E1DCC9' }}>Diagnosis: </b>
                      {turn.reason}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {/* Global Loading Bubble only when initiating or generating probe (not duplicating target bubble) */}
        {currentStatus && !messages.some(m => !m.response) && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            padding: '0.75rem 1.25rem',
            backgroundColor: '#1F150C',
            border: '1px solid #412D15',
            borderRadius: '12px',
            width: 'fit-content'
          }}>
            <Sparkles size={16} color="#D97706" />
            <span style={{ fontSize: '0.82rem', color: '#E1DCC9' }}>{currentStatus}</span>
            <div style={{ display: 'flex', gap: '3px', marginLeft: '4px' }}>
              <span className="typing-dot" style={{ backgroundColor: '#D97706' }}></span>
              <span className="typing-dot" style={{ backgroundColor: '#D97706' }}></span>
              <span className="typing-dot" style={{ backgroundColor: '#D97706' }}></span>
            </div>
          </div>
        )}


        <div ref={scrollEndRef} />
      </div>
    </div>
  );
}
