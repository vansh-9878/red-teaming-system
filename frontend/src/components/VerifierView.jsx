import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  RotateCcw, 
  TrendingDown, 
  ShieldCheck, 
  Cpu, 
  Activity, 
  RefreshCw, 
  Zap, 
  Target, 
  ChevronRight,
  Sliders,
  Filter,
  BarChart2,
  FileCheck,
  Radio
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
  const [tableFilter, setTableFilter] = useState('all');

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
          gap: '0.4rem',
          backgroundColor: 'rgba(5, 150, 105, 0.15)',
          color: '#34D399',
          padding: '4px 12px',
          borderRadius: '9999px',
          fontSize: '0.74rem',
          fontWeight: 700,
          border: '1px solid rgba(52, 211, 153, 0.35)',
          letterSpacing: '0.02em'
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
          gap: '0.4rem',
          backgroundColor: 'rgba(217, 119, 6, 0.15)',
          color: '#FBBF24',
          padding: '4px 12px',
          borderRadius: '9999px',
          fontSize: '0.74rem',
          fontWeight: 700,
          border: '1px solid rgba(251, 191, 36, 0.35)',
          letterSpacing: '0.02em'
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
          gap: '0.4rem',
          backgroundColor: 'rgba(124, 58, 237, 0.15)',
          color: '#C084FC',
          padding: '4px 12px',
          borderRadius: '9999px',
          fontSize: '0.74rem',
          fontWeight: 700,
          border: '1px solid rgba(192, 132, 252, 0.35)',
          letterSpacing: '0.02em'
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
          gap: '0.4rem',
          backgroundColor: 'rgba(220, 38, 38, 0.15)',
          color: '#F87171',
          padding: '4px 12px',
          borderRadius: '9999px',
          fontSize: '0.74rem',
          fontWeight: 700,
          border: '1px solid rgba(248, 113, 113, 0.35)',
          letterSpacing: '0.02em'
        }}>
          <XCircle size={13} />
          UNMITIGATED ({(rasr * 100).toFixed(1)}% RASR)
        </span>
      );
    }
  };

  const filteredProbes = selectedReport?.probe_results?.filter(p => {
    if (tableFilter === 'all') return true;
    if (tableFilter === 'mitigated') return !p.is_still_breached;
    if (tableFilter === 'breached') return p.is_still_breached;
    return p.category === tableFilter;
  }) || [];

  return (
    <div style={{
      flex: 1,
      backgroundColor: '#0A0603',
      height: '100vh',
      overflowY: 'auto',
      color: '#E8E3D5',
      padding: '1.5rem 2rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1.25rem',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* 1. Header & Quick Verification Toolbar */}
      <div style={{
        background: 'linear-gradient(180deg, #181109 0%, #120C06 100%)',
        border: '1px solid #3A2612',
        borderRadius: '14px',
        padding: '1.25rem 1.5rem',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.25rem' }}>
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                backgroundColor: 'rgba(52, 211, 153, 0.12)',
                border: '1px solid rgba(52, 211, 153, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <ShieldCheck size={20} color="#34D399" />
              </div>
              <div>
                <h1 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#F3EFE0', letterSpacing: '-0.02em', margin: 0 }}>
                  Module 7: Patch Verifier & RASR Engine
                </h1>
                <p style={{ fontSize: '0.78rem', color: '#9E9482', margin: '2px 0 0' }}>
                  Headline Defense Metric: Proves automated patch efficacy, residual attack rates & cross-category regression safety.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Action Toolbar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
            {/* Replay Count Selector */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              backgroundColor: '#0F0904',
              border: '1px solid #2F1E0E',
              borderRadius: '8px',
              padding: '3px 8px',
              fontSize: '0.74rem'
            }}>
              <Sliders size={12} color="#D97706" />
              <span style={{ color: '#8C8271' }}>Replays:</span>
              {[2, 3, 5].map(cnt => (
                <button
                  key={cnt}
                  onClick={() => setReplaysCount(cnt)}
                  style={{
                    border: 'none',
                    padding: '2px 7px',
                    borderRadius: '4px',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    backgroundColor: replaysCount === cnt ? '#D97706' : 'transparent',
                    color: replaysCount === cnt ? '#000000' : '#A89E8C',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {cnt}
                </button>
              ))}
            </div>

            {/* Cross Check Toggle */}
            <button
              onClick={() => setCrossCheck(!crossCheck)}
              title="Replay cross-check samples from all other agents"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                backgroundColor: crossCheck ? 'rgba(52, 211, 153, 0.12)' : '#0F0904',
                border: `1px solid ${crossCheck ? 'rgba(52, 211, 153, 0.35)' : '#2F1E0E'}`,
                color: crossCheck ? '#34D399' : '#8C8271',
                borderRadius: '8px',
                padding: '5px 10px',
                fontSize: '0.74rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <Radio size={12} />
              Cross-Check: {crossCheck ? 'ON' : 'OFF'}
            </button>

            {/* Run Verification Button */}
            <button
              onClick={handleRunVerification}
              disabled={isVerifying}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                background: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
                color: '#000000',
                border: 'none',
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: isVerifying ? 'not-allowed' : 'pointer',
                boxShadow: '0 2px 8px rgba(217, 119, 6, 0.3)',
                transition: 'all 0.15s ease'
              }}
            >
              <Zap size={14} className={isVerifying ? 'spin' : ''} />
              {isVerifying ? 'Evaluating RASR...' : 'Run RASR Verification'}
            </button>

            {/* Refresh */}
            <button
              onClick={fetchVerificationData}
              disabled={isLoading || isVerifying}
              title="Refresh Telemetry"
              style={{
                background: '#1A1209',
                color: '#A89E8C',
                border: '1px solid #3A2612',
                padding: '6px 10px',
                borderRadius: '8px',
                cursor: (isLoading || isVerifying) ? 'not-allowed' : 'pointer'
              }}
            >
              <RefreshCw size={13} className={isLoading ? 'spin' : ''} />
            </button>

            {/* Reset */}
            <button
              onClick={handleResetHistory}
              disabled={isVerifying || history.length === 0}
              title="Reset verification history"
              style={{
                background: '#1A1209',
                color: '#8C8271',
                border: '1px solid #3A2612',
                padding: '6px 10px',
                borderRadius: '8px',
                cursor: (isVerifying || history.length === 0) ? 'not-allowed' : 'pointer'
              }}
            >
              <RotateCcw size={13} />
            </button>
          </div>
        </div>
      </div>

      {/* 2. Headline Metric KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        {/* Card 1: Current Overall RASR */}
        <div style={{
          background: 'linear-gradient(145deg, #160F08 0%, #100A05 100%)',
          border: '1px solid #36220E',
          borderRadius: '12px',
          padding: '1.15rem',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#A39987', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Current Overall RASR
            </span>
            <div style={{
              padding: '3px 8px',
              borderRadius: '9999px',
              backgroundColor: chartData?.current_rasr === 0 ? 'rgba(52, 211, 153, 0.15)' : 'rgba(245, 158, 11, 0.15)',
              color: chartData?.current_rasr === 0 ? '#34D399' : '#FBBF24',
              fontSize: '0.68rem',
              fontWeight: 700
            }}>
              {chartData?.current_rasr === 0 ? 'Residual: 0%' : 'Residual Risk'}
            </div>
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: chartData?.current_rasr === 0 ? '#34D399' : '#FBBF24', fontFamily: 'monospace', letterSpacing: '-0.02em' }}>
            {chartData ? `${(chartData.current_rasr * 100).toFixed(1)}%` : '0.0%'}
          </div>
          <div style={{ width: '100%', height: '4px', backgroundColor: '#22150A', borderRadius: '2px', margin: '0.5rem 0 0.35rem', overflow: 'hidden' }}>
            <div style={{
              width: `${chartData ? Math.max(chartData.current_rasr * 100, 3) : 0}%`,
              height: '100%',
              backgroundColor: chartData?.current_rasr === 0 ? '#34D399' : '#FBBF24',
              borderRadius: '2px',
              transition: 'width 0.4s ease'
            }} />
          </div>
          <div style={{ fontSize: '0.7rem', color: '#7E7565' }}>
            Fraction of adversarial probes that still penetrate
          </div>
        </div>

        {/* Card 2: Average Mitigation Rate */}
        <div style={{
          background: 'linear-gradient(145deg, #160F08 0%, #100A05 100%)',
          border: '1px solid #36220E',
          borderRadius: '12px',
          padding: '1.15rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#A39987', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Mean Mitigation Rate
            </span>
            <ShieldCheck size={16} color="#34D399" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F3EFE0', fontFamily: 'monospace', letterSpacing: '-0.02em' }}>
            {chartData ? `${(chartData.average_mitigation_rate * 100).toFixed(1)}%` : '100.0%'}
          </div>
          <div style={{ width: '100%', height: '4px', backgroundColor: '#22150A', borderRadius: '2px', margin: '0.5rem 0 0.35rem', overflow: 'hidden' }}>
            <div style={{
              width: `${chartData ? chartData.average_mitigation_rate * 100 : 100}%`,
              height: '100%',
              backgroundColor: '#34D399',
              borderRadius: '2px',
              transition: 'width 0.4s ease'
            }} />
          </div>
          <div style={{ fontSize: '0.7rem', color: '#7E7565' }}>
            Average vulnerability sealed across all patches
          </div>
        </div>

        {/* Card 3: Fully Mitigated Ratio */}
        <div style={{
          background: 'linear-gradient(145deg, #160F08 0%, #100A05 100%)',
          border: '1px solid #36220E',
          borderRadius: '12px',
          padding: '1.15rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#A39987', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Fully Sealed Patches
            </span>
            <CheckCircle2 size={16} color="#34D399" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F3EFE0', fontFamily: 'monospace', letterSpacing: '-0.02em' }}>
            {chartData ? `${chartData.fully_mitigated_count} / ${chartData.total_patches_verified}` : '0 / 0'}
          </div>
          <div style={{ width: '100%', height: '4px', backgroundColor: '#22150A', borderRadius: '2px', margin: '0.5rem 0 0.35rem', overflow: 'hidden' }}>
            <div style={{
              width: `${chartData && chartData.total_patches_verified > 0 ? (chartData.fully_mitigated_count / chartData.total_patches_verified) * 100 : 0}%`,
              height: '100%',
              backgroundColor: '#10B981',
              borderRadius: '2px',
              transition: 'width 0.4s ease'
            }} />
          </div>
          <div style={{ fontSize: '0.7rem', color: '#7E7565' }}>
            Patches achieving 100% defense resilience
          </div>
        </div>

        {/* Card 4: Total Replay Audit Tests */}
        <div style={{
          background: 'linear-gradient(145deg, #160F08 0%, #100A05 100%)',
          border: '1px solid #36220E',
          borderRadius: '12px',
          padding: '1.15rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#A39987', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Replayed Probes Tested
            </span>
            <Activity size={16} color="#D97706" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F3EFE0', fontFamily: 'monospace', letterSpacing: '-0.02em' }}>
            {history.reduce((acc, r) => acc + (r.replayed_probes_count || 0), 0)}
          </div>
          <div style={{ width: '100%', height: '4px', backgroundColor: '#22150A', borderRadius: '2px', margin: '0.5rem 0 0.35rem', overflow: 'hidden' }}>
            <div style={{ width: '100%', height: '100%', backgroundColor: '#D97706', borderRadius: '2px' }} />
          </div>
          <div style={{ fontSize: '0.7rem', color: '#7E7565' }}>
            High-harm mutated & cross-category test cases
          </div>
        </div>
      </div>

      {/* 3. Longitudinal RASR Progression Chart (Executive Visualizer) */}
      <div style={{
        background: 'linear-gradient(180deg, #140D07 0%, #0E0804 100%)',
        border: '1px solid #32210F',
        borderRadius: '14px',
        padding: '1.35rem 1.5rem',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 800, color: '#F3EFE0', display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
              <TrendingDown size={17} color="#D97706" />
              Longitudinal RASR Timeline (Headline Defense Metric)
            </h2>
            <p style={{ fontSize: '0.74rem', color: '#8C8271', margin: '2px 0 0' }}>
              Measures how residual breach probability systematically drops as sequential patches are deployed.
            </p>
          </div>

          {/* Interactive Patch Selector Pills */}
          {chartData?.timeline?.length > 0 && (
            <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
              {chartData.timeline.map((point) => {
                const isSelected = selectedReport && selectedReport.patch_id === point.patch_id;
                return (
                  <button
                    key={point.patch_index}
                    onClick={() => {
                      const matched = history.find(h => h.patch_id === point.patch_id);
                      if (matched) setSelectedReportId(matched.verification_id);
                    }}
                    style={{
                      border: `1px solid ${isSelected ? '#F59E0B' : '#2E1E0E'}`,
                      backgroundColor: isSelected ? 'rgba(245, 158, 11, 0.18)' : '#120B05',
                      color: isSelected ? '#FBBF24' : '#A39987',
                      padding: '3px 10px',
                      borderRadius: '6px',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    {point.label}: {(point.overall_rasr * 100).toFixed(0)}% RASR
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Visual Columns Container */}
        {chartData && chartData.timeline && chartData.timeline.length > 0 ? (
          <div>
            <div style={{
              display: 'grid',
              gridTemplateColumns: `repeat(${chartData.timeline.length}, 1fr)`,
              gap: '1.25rem',
              alignItems: 'flex-end',
              height: '190px',
              borderBottom: '1px solid #291A0C',
              paddingBottom: '0.85rem'
            }}>
              {chartData.timeline.map((point) => {
                const heightPercent = Math.max(Math.round((1 - point.overall_rasr) * 100), 14);
                const rasrPercent = (point.overall_rasr * 100).toFixed(0);
                const isSelected = selectedReport && selectedReport.patch_id === point.patch_id;
                const isZero = point.overall_rasr === 0;

                return (
                  <div
                    key={point.patch_index}
                    onClick={() => {
                      const matched = history.find(h => h.patch_id === point.patch_id);
                      if (matched) setSelectedReportId(matched.verification_id);
                    }}
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
                      fontSize: '0.74rem',
                      fontWeight: 800,
                      fontFamily: 'monospace',
                      color: isZero ? '#34D399' : (point.overall_rasr < 0.5 ? '#FBBF24' : '#F87171'),
                      marginBottom: '6px'
                    }}>
                      {rasrPercent}% RASR
                    </div>
                    <div style={{
                      width: '100%',
                      maxWidth: '68px',
                      height: `${heightPercent}%`,
                      background: isZero
                        ? 'linear-gradient(180deg, #10B981 0%, #059669 100%)'
                        : (point.overall_rasr < 0.5
                          ? 'linear-gradient(180deg, #F59E0B 0%, #B45309 100%)'
                          : 'linear-gradient(180deg, #EF4444 0%, #B91C1C 100%)'),
                      borderRadius: '8px 8px 0 0',
                      border: isSelected ? '2px solid #FFFFFF' : '1px solid rgba(255,255,255,0.08)',
                      boxShadow: isSelected ? '0 0 16px rgba(245, 158, 11, 0.4)' : 'none',
                      transition: 'all 0.2s ease',
                      position: 'relative'
                    }}>
                      <div style={{
                        position: 'absolute',
                        bottom: '6px',
                        left: 0,
                        right: 0,
                        textAlign: 'center',
                        fontSize: '0.7rem',
                        fontWeight: 800,
                        color: '#000000'
                      }}>
                        {(point.mitigation_rate * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Labels under the columns */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: `repeat(${chartData.timeline.length}, 1fr)`,
              gap: '1.25rem',
              textAlign: 'center',
              marginTop: '0.65rem'
            }}>
              {chartData.timeline.map((point) => (
                <div key={point.patch_index}>
                  <div style={{ fontWeight: 800, color: '#F3EFE0', fontSize: '0.78rem' }}>{point.label}</div>
                  <div style={{ fontSize: '0.7rem', color: '#8C8271', textTransform: 'capitalize' }}>
                    {point.primary_category}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '2.75rem 1rem',
            color: '#8C8271',
            backgroundColor: '#0A0603',
            borderRadius: '10px',
            border: '1px dashed #2E1E0E'
          }}>
            <ShieldCheck size={32} color="#3A2612" style={{ margin: '0 auto 0.5rem' }} />
            <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#A89E8C' }}>
              No Verification History Logged Yet
            </div>
            <div style={{ fontSize: '0.74rem', marginTop: '0.25rem', color: '#7E7565' }}>
              Launch a campaign or click <strong>Run RASR Verification</strong> above to evaluate active patches.
            </div>
          </div>
        )}
      </div>

      {/* 4. Selected Verification Report Deep-Dive */}
      {selectedReport && (
        <div style={{
          background: 'linear-gradient(180deg, #160F08 0%, #100A05 100%)',
          border: '1px solid #36220E',
          borderRadius: '14px',
          padding: '1.35rem 1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.15rem',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)'
        }}>
          {/* Report Top Banner */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #291A0C', paddingBottom: '0.85rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F3EFE0', margin: 0 }}>
                  Audit Details: {selectedReport.patch_id || 'Active Defense Patch'}
                </h3>
                {getVerdictBadge(selectedReport.verdict, selectedReport.overall_rasr)}
              </div>
              <p style={{ fontSize: '0.75rem', color: '#9E9482', margin: 0 }}>
                Target Chatbot: <strong style={{ color: '#E8E3D5' }}>{selectedReport.target_model}</strong> ({selectedReport.target_provider}) | Primary Category: <strong style={{ textTransform: 'capitalize', color: '#F59E0B' }}>{selectedReport.primary_category}</strong> | Technique: <code style={{ backgroundColor: '#1F140A', padding: '2px 6px', borderRadius: '4px', color: '#E1DCC9' }}>{selectedReport.patch_type}</code>
              </p>
            </div>

            <div style={{ textAlign: 'right', fontSize: '0.75rem', color: '#7E7565' }}>
              <div>{new Date((selectedReport.timestamp || Date.now() / 1000) * 1000).toLocaleTimeString()}</div>
              <div style={{ fontWeight: 700, color: '#A89E8C' }}>{selectedReport.replayed_probes_count} Replayed Probes</div>
            </div>
          </div>

          {/* Per-Category Cross-Check Breakdown Cards */}
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#A39987', textTransform: 'uppercase', marginBottom: '0.45rem', letterSpacing: '0.04em' }}>
              Per-Category Safety Breakdown (Regression Cross-Check)
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
              {/* Primary Category */}
              <div style={{
                background: 'linear-gradient(145deg, #1F1409 0%, #170E06 100%)',
                border: '1px solid #5A3A17',
                borderRadius: '10px',
                padding: '0.75rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#F59E0B', textTransform: 'capitalize' }}>
                    🎯 {selectedReport.primary_category} (Primary)
                  </span>
                  <span style={{ fontSize: '0.76rem', fontWeight: 800, fontFamily: 'monospace', color: selectedReport.primary_category_rasr === 0 ? '#34D399' : '#FBBF24' }}>
                    {(selectedReport.primary_category_rasr * 100).toFixed(0)}% RASR
                  </span>
                </div>
                <div style={{ width: '100%', height: '3px', backgroundColor: '#2C1B0B', borderRadius: '2px', margin: '0.45rem 0 0.25rem' }}>
                  <div style={{
                    width: `${selectedReport.primary_category_rasr === 0 ? 100 : (1 - selectedReport.primary_category_rasr) * 100}%`,
                    height: '100%',
                    backgroundColor: selectedReport.primary_category_rasr === 0 ? '#34D399' : '#FBBF24',
                    borderRadius: '2px'
                  }} />
                </div>
                <div style={{ fontSize: '0.68rem', color: '#7E7565' }}>
                  Mitigation: {selectedReport.primary_category_rasr === 0 ? '100% Sealed' : 'Partial risk'}
                </div>
              </div>

              {/* Cross Categories */}
              {selectedReport.cross_category_rasrs && Object.entries(selectedReport.cross_category_rasrs).map(([catKey, catVal]) => {
                const catRasr = typeof catVal === 'object' ? catVal.rasr : catVal;
                const isSafe = catRasr === 0;
                return (
                  <div key={catKey} style={{
                    background: 'linear-gradient(145deg, #140D07 0%, #0E0804 100%)',
                    border: '1px solid #2B1B0C',
                    borderRadius: '10px',
                    padding: '0.75rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#A89E8C', textTransform: 'capitalize' }}>
                        🛡️ {catKey}
                      </span>
                      <span style={{ fontSize: '0.76rem', fontWeight: 800, fontFamily: 'monospace', color: isSafe ? '#34D399' : '#FBBF24' }}>
                        {(catRasr * 100).toFixed(0)}% RASR
                      </span>
                    </div>
                    <div style={{ width: '100%', height: '3px', backgroundColor: '#22150A', borderRadius: '2px', margin: '0.45rem 0 0.25rem' }}>
                      <div style={{
                        width: `${(1 - catRasr) * 100}%`,
                        height: '100%',
                        backgroundColor: isSafe ? '#34D399' : '#FBBF24',
                        borderRadius: '2px'
                      }} />
                    </div>
                    <div style={{ fontSize: '0.68rem', color: '#7E7565' }}>
                      Cross-Safety: {isSafe ? 'Regression-Safe' : 'Leak detected'}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Coordinator Feedback Telemetry Box */}
          {selectedReport.coordinator_feedback && selectedReport.coordinator_feedback.explanation && (
            <div style={{
              background: 'linear-gradient(145deg, #1B130A 0%, #130C05 100%)',
              border: '1px solid #3E2914',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.65rem'
            }}>
              <Cpu size={18} color="#D97706" style={{ flexShrink: 0 }} />
              <div style={{ fontSize: '0.76rem', color: '#E8E3D5' }}>
                <strong style={{ color: '#FBBF24' }}>Coordinator Bandit Feedback: </strong>
                {selectedReport.coordinator_feedback.explanation}
              </div>
            </div>
          )}

          {/* Replayed Probes Granular Table & Filters */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.55rem' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#A39987', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Granular Probe Replay Execution Audit ({selectedReport.probe_results?.length || 0} Test Cases)
              </div>

              {/* Table Filter Pills */}
              <div style={{ display: 'flex', gap: '0.35rem', fontSize: '0.72rem' }}>
                {['all', 'mitigated', 'breached'].map(f => (
                  <button
                    key={f}
                    onClick={() => setTableFilter(f)}
                    style={{
                      border: 'none',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '0.7rem',
                      fontWeight: 700,
                      textTransform: 'capitalize',
                      cursor: 'pointer',
                      backgroundColor: tableFilter === f ? '#3E2914' : 'transparent',
                      color: tableFilter === f ? '#FBBF24' : '#7E7565'
                    }}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            <div style={{
              backgroundColor: '#080502',
              border: '1px solid #2B1B0C',
              borderRadius: '10px',
              overflow: 'hidden'
            }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '110px 1fr 1fr 90px 100px',
                padding: '0.65rem 0.95rem',
                backgroundColor: '#120B05',
                borderBottom: '1px solid #2B1B0C',
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#8C8271',
                textTransform: 'uppercase'
              }}>
                <div>Category</div>
                <div>Replayed Probe</div>
                <div>Post-Patch Target Reply</div>
                <div style={{ textAlign: 'center' }}>Score</div>
                <div style={{ textAlign: 'right' }}>Outcome</div>
              </div>

              <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
                {filteredProbes.map((p, idx) => (
                  <div key={idx} style={{
                    display: 'grid',
                    gridTemplateColumns: '110px 1fr 1fr 90px 100px',
                    padding: '0.65rem 0.95rem',
                    borderBottom: '1px solid #1A1107',
                    fontSize: '0.75rem',
                    alignItems: 'center',
                    gap: '0.5rem',
                    transition: 'background 0.15s ease'
                  }}>
                    <div style={{ fontWeight: 700, color: '#D97706', textTransform: 'capitalize', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#D97706' }} />
                      {p.category}
                    </div>
                    <div style={{
                      color: '#F3EFE0',
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
                    <div style={{ textAlign: 'center', fontFamily: 'monospace', fontWeight: 800, color: p.post_patch_score < 0.6 ? '#34D399' : '#F87171' }}>
                      {p.post_patch_score.toFixed(2)}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      {p.is_still_breached ? (
                        <span style={{
                          backgroundColor: 'rgba(239, 68, 68, 0.15)',
                          color: '#F87171',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontWeight: 700,
                          fontSize: '0.68rem',
                          border: '1px solid rgba(239, 68, 68, 0.3)'
                        }}>
                          BREACHED
                        </span>
                      ) : (
                        <span style={{
                          backgroundColor: 'rgba(52, 211, 153, 0.15)',
                          color: '#34D399',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontWeight: 700,
                          fontSize: '0.68rem',
                          border: '1px solid rgba(52, 211, 153, 0.3)'
                        }}>
                          MITIGATED
                        </span>
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
