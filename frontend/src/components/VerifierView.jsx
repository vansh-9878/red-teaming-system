import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  RotateCcw, 
  Play, 
  TrendingDown, 
  ShieldCheck, 
  ShieldAlert, 
  Layers, 
  Cpu, 
  Activity, 
  FileText,
  RefreshCw,
  Zap,
  Target
} from 'lucide-react';

export default function VerifierView({ messages }) {
  const [chartData, setChartData] = useState(null);
  const [history, setHistory] = useState([]);
  const [latestReport, setLatestReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [selectedReportId, setSelectedReportId] = useState(null);
  const [replaysCount, setReplaysCount] = useState(3);
  const [crossCheck, setCrossCheck] = useState(true);

  const fetchVerificationData = async () => {
    setIsLoading(true);
    try {
      const [chartRes, histRes, latestRes] = await Promise.all([
        fetch('http://localhost:8000/verifier/chart-data'),
        fetch('http://localhost:8000/verifier/history'),
        fetch('http://localhost:8000/verifier/latest')
      ]);

      if (chartRes.ok) {
        const cData = await chartRes.json();
        setChartData(cData);
      }
      if (histRes.ok) {
        const hData = await histRes.json();
        setHistory(hData);
        if (hData.length > 0 && !selectedReportId) {
          setSelectedReportId(hData[hData.length - 1].verification_id);
        }
      }
      if (latestRes.ok) {
        const lData = await latestRes.json();
        setLatestReport(lData);
      }
    } catch (err) {
      console.error('Error fetching verification data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVerificationData();
  }, []);

  const handleRunVerification = async () => {
    setIsVerifying(true);
    try {
      const res = await fetch('http://localhost:8000/verifier/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          replays_per_category: replaysCount,
          sample_cross_check: crossCheck
        })
      });
      if (res.ok) {
        const newReport = await res.json();
        setSelectedReportId(newReport.verification_id);
        await fetchVerificationData();
      }
    } catch (err) {
      console.error('Error running verification:', err);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResetHistory = async () => {
    if (window.confirm('Reset all verification logs and RASR timeline history?')) {
      try {
        await fetch('http://localhost:8000/verifier/reset', { method: 'POST' });
        setChartData(null);
        setHistory([]);
        setLatestReport(null);
        setSelectedReportId(null);
      } catch (err) {
        console.error('Error resetting verification history:', err);
      }
    }
  };

  const selectedReport = history.find(r => r.verification_id === selectedReportId) || latestReport;

  const getVerdictBadge = (verdict, rasr) => {
    if (verdict === 'fully_mitigated' || rasr === 0.0) {
      return (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          backgroundColor: '#064E3B',
          color: '#34D399',
          padding: '4px 10px',
          borderRadius: '9999px',
          fontSize: '0.75rem',
          fontWeight: 700,
          border: '1px solid #059669'
        }}>
          <CheckCircle2 size={13} />
          FULLY MITIGATED (0% RASR)
        </span>
      );
    } else if (verdict === 'partially_mitigated' || rasr < 0.5) {
      return (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          backgroundColor: '#78350F',
          color: '#FBBF24',
          padding: '4px 10px',
          borderRadius: '9999px',
          fontSize: '0.75rem',
          fontWeight: 700,
          border: '1px solid #D97706'
        }}>
          <AlertTriangle size={13} />
          PARTIALLY MITIGATED ({(rasr * 100).toFixed(1)}% RASR)
        </span>
      );
    } else if (verdict === 'regression_detected') {
      return (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          backgroundColor: '#4C1D95',
          color: '#C084FC',
          padding: '4px 10px',
          borderRadius: '9999px',
          fontSize: '0.75rem',
          fontWeight: 700,
          border: '1px solid #7C3AED'
        }}>
          <AlertTriangle size={13} />
          REGRESSION DETECTED
        </span>
      );
    } else {
      return (
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          backgroundColor: '#7F1D1D',
          color: '#F87171',
          padding: '4px 10px',
          borderRadius: '9999px',
          fontSize: '0.75rem',
          fontWeight: 700,
          border: '1px solid #DC2626'
        }}>
          <XCircle size={13} />
          UNMITIGATED ({(rasr * 100).toFixed(1)}% RASR)
        </span>
      );
    }
  };

  return (
    <div style={{
      flex: 1,
      backgroundColor: '#0C0804',
      height: '100vh',
      overflowY: 'auto',
      color: '#E1DCC9',
      padding: '1.75rem 2.25rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1.5rem'
    }}>
      {/* View Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #32210F', paddingBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
            <div style={{
              width: '34px',
              height: '34px',
              borderRadius: '8px',
              backgroundColor: '#2F2010',
              border: '1px solid #5E4120',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <ShieldCheck size={19} color="#34D399" />
            </div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#E1DCC9', letterSpacing: '-0.02em' }}>
              Module 7: Patch Verifier & RASR Engine
            </h1>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#A89E8C' }}>
            Measures Residual Attack Success Rate (RASR), proves patch efficacy, executes cross-category regression audits, and feeds feedback to the Coordinator.
          </p>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <button
            onClick={fetchVerificationData}
            disabled={isLoading || isVerifying}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: '#1F150C',
              color: '#A89E8C',
              border: '1px solid #412D15',
              padding: '0.5rem 0.85rem',
              borderRadius: '8px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: (isLoading || isVerifying) ? 'not-allowed' : 'pointer'
            }}
          >
            <RefreshCw size={14} className={isLoading ? 'spin' : ''} />
            Refresh
          </button>

          <button
            onClick={handleRunVerification}
            disabled={isVerifying}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: '#D97706',
              color: '#000000',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: isVerifying ? 'not-allowed' : 'pointer'
            }}
          >
            <Zap size={14} />
            {isVerifying ? 'Verifying Patches...' : 'Run RASR Verification'}
          </button>

          <button
            onClick={handleResetHistory}
            disabled={isVerifying || history.length === 0}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: 'transparent',
              color: '#8E8270',
              border: '1px solid #32210F',
              padding: '0.5rem 0.75rem',
              borderRadius: '8px',
              fontSize: '0.78rem',
              cursor: (isVerifying || history.length === 0) ? 'not-allowed' : 'pointer'
            }}
          >
            <RotateCcw size={13} />
            Reset
          </button>
        </div>
      </div>

      {/* Headline Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        {/* Card 1: Current Overall RASR */}
        <div style={{
          backgroundColor: '#140D07',
          border: '1px solid #32210F',
          borderRadius: '12px',
          padding: '1.15rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
            <span style={{ fontSize: '0.73rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase' }}>
              Current Overall RASR
            </span>
            <TrendingDown size={16} color={chartData?.current_rasr === 0 ? "#34D399" : "#FBBF24"} />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: chartData?.current_rasr === 0 ? '#34D399' : '#FBBF24', fontFamily: 'monospace' }}>
            {chartData ? `${(chartData.current_rasr * 100).toFixed(1)}%` : '0.0%'}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#8E8270', marginTop: '0.25rem' }}>
            Baseline ASR: 100% → Residual ASR post-patch
          </div>
        </div>

        {/* Card 2: Average Mitigation Rate */}
        <div style={{
          backgroundColor: '#140D07',
          border: '1px solid #32210F',
          borderRadius: '12px',
          padding: '1.15rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
            <span style={{ fontSize: '0.73rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase' }}>
              Average Mitigation Rate
            </span>
            <ShieldCheck size={16} color="#34D399" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#E1DCC9', fontFamily: 'monospace' }}>
            {chartData ? `${(chartData.average_mitigation_rate * 100).toFixed(1)}%` : '100.0%'}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#8E8270', marginTop: '0.25rem' }}>
            Mean breach reduction across patches
          </div>
        </div>

        {/* Card 3: Fully Mitigated Ratio */}
        <div style={{
          backgroundColor: '#140D07',
          border: '1px solid #32210F',
          borderRadius: '12px',
          padding: '1.15rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
            <span style={{ fontSize: '0.73rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase' }}>
              Fully Mitigated Patches
            </span>
            <CheckCircle2 size={16} color="#34D399" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#E1DCC9', fontFamily: 'monospace' }}>
            {chartData ? `${chartData.fully_mitigated_count} / ${chartData.total_patches_verified}` : '0 / 0'}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#8E8270', marginTop: '0.25rem' }}>
            Patches with 0.0% residual breach rate
          </div>
        </div>

        {/* Card 4: Total Replay Audit Tests */}
        <div style={{
          backgroundColor: '#140D07',
          border: '1px solid #32210F',
          borderRadius: '12px',
          padding: '1.15rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
            <span style={{ fontSize: '0.73rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase' }}>
              Total Replayed Probes
            </span>
            <Activity size={16} color="#D97706" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#E1DCC9', fontFamily: 'monospace' }}>
            {history.reduce((acc, r) => acc + (r.replayed_probes_count || 0), 0)}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#8E8270', marginTop: '0.25rem' }}>
            Mutated + cross-category test cases
          </div>
        </div>
      </div>

      {/* Main Longitudinal RASR Progression Chart */}
      <div style={{
        backgroundColor: '#140D07',
        border: '1px solid #32210F',
        borderRadius: '12px',
        padding: '1.5rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 800, color: '#E1DCC9', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingDown size={17} color="#D97706" />
              Longitudinal RASR Timeline (Headline Defense Metric)
            </h2>
            <p style={{ fontSize: '0.75rem', color: '#8E8270' }}>
              Tracks Residual Attack Success Rate as consecutive patches are deployed (Patch #1 → Patch #2 → …).
            </p>
          </div>

          {/* Category Chips */}
          <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.72rem' }}>
            <span style={{ padding: '3px 8px', borderRadius: '4px', backgroundColor: '#1F150C', color: '#FBBF24', border: '1px solid #5E4120' }}>
              Overall RASR
            </span>
            <span style={{ padding: '3px 8px', borderRadius: '4px', backgroundColor: '#1F150C', color: '#34D399', border: '1px solid #059669' }}>
              Persona
            </span>
            <span style={{ padding: '3px 8px', borderRadius: '4px', backgroundColor: '#1F150C', color: '#60A5FA', border: '1px solid #2563EB' }}>
              Persuasion
            </span>
            <span style={{ padding: '3px 8px', borderRadius: '4px', backgroundColor: '#1F150C', color: '#C084FC', border: '1px solid #7C3AED' }}>
              Escalation
            </span>
            <span style={{ padding: '3px 8px', borderRadius: '4px', backgroundColor: '#1F150C', color: '#F87171', border: '1px solid #DC2626' }}>
              Obfuscation
            </span>
          </div>
        </div>

        {/* Timeline Visualization */}
        {chartData && chartData.timeline && chartData.timeline.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Visual Bars Container */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: `repeat(${chartData.timeline.length}, 1fr)`,
              gap: '1rem',
              alignItems: 'flex-end',
              height: '180px',
              borderBottom: '1px solid #32210F',
              paddingBottom: '0.75rem'
            }}>
              {chartData.timeline.map((point) => {
                const heightPercent = Math.max(Math.round((1 - point.overall_rasr) * 100), 12);
                const rasrPercent = (point.overall_rasr * 100).toFixed(0);
                const isSelected = selectedReport && selectedReport.patch_id === point.patch_id;

                return (
                  <div
                    key={point.patch_index}
                    onClick={() => setSelectedReportId(point.patch_id ? history.find(h => h.patch_id === point.patch_id)?.verification_id : null)}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'flex-end',
                      height: '100%',
                      cursor: 'pointer'
                    }}
                  >
                    <div style={{
                      fontSize: '0.72rem',
                      fontWeight: 800,
                      fontFamily: 'monospace',
                      color: point.overall_rasr === 0 ? '#34D399' : '#FBBF24',
                      marginBottom: '4px'
                    }}>
                      {rasrPercent}% RASR
                    </div>
                    <div style={{
                      width: '100%',
                      maxWidth: '54px',
                      height: `${heightPercent}%`,
                      backgroundColor: point.overall_rasr === 0 ? '#059669' : (point.overall_rasr < 0.5 ? '#D97706' : '#DC2626'),
                      borderRadius: '6px 6px 0 0',
                      border: isSelected ? '2px solid #FFFFFF' : '1px solid transparent',
                      transition: 'all 0.2s ease',
                      position: 'relative'
                    }}>
                      <div style={{
                        position: 'absolute',
                        bottom: '4px',
                        left: 0,
                        right: 0,
                        textAlign: 'center',
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        color: '#000000'
                      }}>
                        {(point.mitigation_rate * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Labels under the bars */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: `repeat(${chartData.timeline.length}, 1fr)`,
              gap: '1rem',
              textAlign: 'center'
            }}>
              {chartData.timeline.map((point) => (
                <div key={point.patch_index} style={{ fontSize: '0.75rem' }}>
                  <div style={{ fontWeight: 700, color: '#E1DCC9' }}>{point.label}</div>
                  <div style={{ fontSize: '0.68rem', color: '#8E8270', textTransform: 'capitalize' }}>
                    {point.primary_category}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '2.5rem 1rem',
            color: '#8E8270',
            backgroundColor: '#0C0804',
            borderRadius: '8px',
            border: '1px dashed #32210F'
          }}>
            <ShieldCheck size={28} color="#412D15" style={{ margin: '0 auto 0.5rem' }} />
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#A89E8C' }}>
              No Verification History Logged Yet
            </div>
            <div style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
              Launch a Red-Teaming Campaign or click <strong>Run RASR Verification</strong> above to evaluate active patches.
            </div>
          </div>
        )}
      </div>

      {/* Selected Verification Report Deep-Dive */}
      {selectedReport && (
        <div style={{
          backgroundColor: '#140D07',
          border: '1px solid #32210F',
          borderRadius: '12px',
          padding: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem'
        }}>
          {/* Report Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #2F2010', paddingBottom: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#E1DCC9' }}>
                  Verification Audit: {selectedReport.patch_id || 'Latest Patch'}
                </h3>
                {getVerdictBadge(selectedReport.verdict, selectedReport.overall_rasr)}
              </div>
              <p style={{ fontSize: '0.75rem', color: '#A89E8C' }}>
                Target: <strong>{selectedReport.target_model}</strong> ({selectedReport.target_provider}) | Primary Vulnerability: <strong style={{ textTransform: 'capitalize' }}>{selectedReport.primary_category}</strong> | Patch Technique: <code>{selectedReport.patch_type}</code>
              </p>
            </div>

            <div style={{ textAlign: 'right', fontSize: '0.78rem', color: '#8E8270' }}>
              <div>{new Date((selectedReport.timestamp || Date.now() / 1000) * 1000).toLocaleTimeString()}</div>
              <div style={{ fontWeight: 600, color: '#A89E8C' }}>{selectedReport.replayed_probes_count} Replayed Probes</div>
            </div>
          </div>

          {/* Category Breakdown Chips */}
          <div>
            <div style={{ fontSize: '0.73rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
              Per-Category Mitigation Breakdown (Cross-Check Safety)
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
              {/* Primary Category */}
              <div style={{
                backgroundColor: '#1F150C',
                border: '1px solid #5E4120',
                borderRadius: '8px',
                padding: '0.75rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#D97706', textTransform: 'capitalize' }}>
                    🎯 {selectedReport.primary_category} (Primary)
                  </span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 800, fontFamily: 'monospace', color: selectedReport.primary_category_rasr === 0 ? '#34D399' : '#FBBF24' }}>
                    {(selectedReport.primary_category_rasr * 100).toFixed(0)}% RASR
                  </span>
                </div>
                <div style={{ fontSize: '0.68rem', color: '#8E8270', marginTop: '0.2rem' }}>
                  Status: {selectedReport.primary_category_rasr === 0 ? 'Sealed' : 'Residual risk'}
                </div>
              </div>

              {/* Cross Categories */}
              {selectedReport.cross_category_rasrs && Object.entries(selectedReport.cross_category_rasrs).map(([catKey, catVal]) => {
                const catRasr = typeof catVal === 'object' ? catVal.rasr : catVal;
                return (
                  <div key={catKey} style={{
                    backgroundColor: '#140D07',
                    border: '1px solid #32210F',
                    borderRadius: '8px',
                    padding: '0.75rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#A89E8C', textTransform: 'capitalize' }}>
                        🛡️ {catKey}
                      </span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 800, fontFamily: 'monospace', color: catRasr === 0 ? '#34D399' : '#FBBF24' }}>
                        {(catRasr * 100).toFixed(0)}% RASR
                      </span>
                    </div>
                    <div style={{ fontSize: '0.68rem', color: '#8E8270', marginTop: '0.2rem' }}>
                      Status: {catRasr === 0 ? 'Reg-Safe' : 'Leak detected'}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Coordinator Feedback Telemetry */}
          {selectedReport.coordinator_feedback && selectedReport.coordinator_feedback.explanation && (
            <div style={{
              backgroundColor: '#1C150E',
              border: '1px solid #412D15',
              borderRadius: '8px',
              padding: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem'
            }}>
              <Cpu size={16} color="#D97706" style={{ flexShrink: 0 }} />
              <div style={{ fontSize: '0.75rem', color: '#E1DCC9' }}>
                <strong style={{ color: '#FBBF24' }}>Coordinator Bandit Feedback: </strong>
                {selectedReport.coordinator_feedback.explanation}
              </div>
            </div>
          )}

          {/* Replayed Probes Granular Table */}
          <div>
            <div style={{ fontSize: '0.73rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
              Granular Probe Replay Execution Audit ({selectedReport.probe_results?.length || 0} Test Cases)
            </div>
            <div style={{
              backgroundColor: '#0C0804',
              border: '1px solid #2F2010',
              borderRadius: '8px',
              overflow: 'hidden'
            }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '110px 1fr 1fr 100px 90px',
                padding: '0.6rem 0.85rem',
                backgroundColor: '#140D07',
                borderBottom: '1px solid #2F2010',
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#8E8270',
                textTransform: 'uppercase'
              }}>
                <div>Category</div>
                <div>Replayed Probe</div>
                <div>Post-Patch Target Reply</div>
                <div style={{ textAlign: 'center' }}>Score</div>
                <div style={{ textAlign: 'right' }}>Outcome</div>
              </div>

              <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
                {selectedReport.probe_results && selectedReport.probe_results.map((p, idx) => (
                  <div key={idx} style={{
                    display: 'grid',
                    gridTemplateColumns: '110px 1fr 1fr 100px 90px',
                    padding: '0.65rem 0.85rem',
                    borderBottom: '1px solid #1F150C',
                    fontSize: '0.75rem',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <div style={{ fontWeight: 600, color: '#D97706', textTransform: 'capitalize' }}>
                      {p.category}
                    </div>
                    <div style={{
                      color: '#E1DCC9',
                      fontFamily: 'monospace',
                      fontSize: '0.72rem',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }} title={p.probe}>
                      {p.probe}
                    </div>
                    <div style={{
                      color: '#A89E8C',
                      fontSize: '0.72rem',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }} title={p.post_patch_response}>
                      {p.post_patch_response}
                    </div>
                    <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 700, color: p.post_patch_score < 0.6 ? '#34D399' : '#F87171' }}>
                      {p.post_patch_score.toFixed(2)}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      {p.is_still_breached ? (
                        <span style={{ color: '#F87171', fontWeight: 700, fontSize: '0.7rem' }}>BREACHED</span>
                      ) : (
                        <span style={{ color: '#34D399', fontWeight: 700, fontSize: '0.7rem' }}>MITIGATED</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
