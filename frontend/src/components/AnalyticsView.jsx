import React from 'react';
import { 
  BarChart3, 
  ShieldAlert, 
  ShieldCheck, 
  Activity, 
  Zap, 
  Scale, 
  Award,
  Layers
} from 'lucide-react';

export default function AnalyticsView({
  banditState,
  campaignSummary,
  totalRounds
}) {
  const arms = banditState?.arms || {};
  const armKeys = ['persona', 'persuasion', 'escalation', 'obfuscation'];
  const fp = campaignSummary?.fingerprint;

  const totalBreaches = campaignSummary?.total_breaches || 0;
  const completedRounds = campaignSummary?.total_tries || banditState?.total_rounds || 0;
  const maxHarm = campaignSummary?.max_harm_score || 0;
  const asr = completedRounds > 0 ? ((totalBreaches / completedRounds) * 100).toFixed(1) : '0.0';

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
      {/* Page Header */}
      <div style={{ marginBottom: '1.75rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#E1DCC9', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <BarChart3 size={24} color="#D97706" />
          Campaign Analytics & Vulnerability Fingerprint
        </h2>
        <p style={{ fontSize: '0.82rem', color: '#A89E8C', marginTop: '0.25rem' }}>
          Comprehensive evaluation metrics, Multi-Armed Bandit weights, and model risk breakdown.
        </p>
      </div>

      {/* 1. Top Metrics KPI Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.75rem' }}>
        <div style={{
          backgroundColor: '#1F150C',
          border: '1px solid #412D15',
          borderRadius: '12px',
          padding: '1.1rem',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase' }}>
            Total Rounds
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#E1DCC9', marginTop: '0.2rem' }}>
            {completedRounds} <span style={{ fontSize: '0.9rem', color: '#8E8270' }}>/ {totalRounds}</span>
          </div>
        </div>

        <div style={{
          backgroundColor: '#1F150C',
          border: `1px solid ${totalBreaches > 0 ? '#E63946' : '#412D15'}`,
          borderRadius: '12px',
          padding: '1.1rem',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase' }}>
            Breaches Detected
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: totalBreaches > 0 ? '#E63946' : '#2A9D8F', marginTop: '0.2rem' }}>
            {totalBreaches}
          </div>
        </div>

        <div style={{
          backgroundColor: '#1F150C',
          border: '1px solid #412D15',
          borderRadius: '12px',
          padding: '1.1rem',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase' }}>
            Attack Success Rate (ASR)
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#D97706', marginTop: '0.2rem' }}>
            {asr}%
          </div>
        </div>

        <div style={{
          backgroundColor: '#1F150C',
          border: '1px solid #412D15',
          borderRadius: '12px',
          padding: '1.1rem',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#A89E8C', textTransform: 'uppercase' }}>
            Max Harm Score
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: maxHarm >= 0.6 ? '#E63946' : '#2A9D8F', marginTop: '0.2rem' }}>
            {maxHarm.toFixed(2)}
          </div>
        </div>
      </div>

      {/* 2. UCB Bandit Weights Panel */}
      <div style={{
        backgroundColor: '#1F150C',
        border: '1px solid #412D15',
        borderRadius: '14px',
        padding: '1.5rem',
        marginBottom: '1.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#E1DCC9' }}>
              Multi-Armed Bandit Arms & Upper Confidence Bounds (UCB1)
            </h3>
            <p style={{ fontSize: '0.75rem', color: '#A89E8C' }}>
              Real-time exploration vs exploitation weights controlling specialist agent selection.
            </p>
          </div>
          <span style={{ fontSize: '0.75rem', color: '#D97706', fontFamily: 'monospace' }}>
            Novelty Rule: STAR 2026 Active
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
          {armKeys.map((k) => {
            const arm = arms[k] || { name: k, ucb_score: 999, pulls: 0, mean_reward: 0, win_count: 0 };
            const ucbDisplay = arm.ucb_score < 100 ? arm.ucb_score.toFixed(3) : 'Inf';

            return (
              <div key={k} style={{
                backgroundColor: '#140D07',
                border: '1px solid #32210F',
                borderRadius: '10px',
                padding: '1rem'
              }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#E1DCC9', marginBottom: '0.35rem' }}>
                  {arm.name}
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.35rem', marginBottom: '0.6rem' }}>
                  <span style={{ fontSize: '1.5rem', fontWeight: 800, color: '#D97706', fontFamily: 'monospace' }}>
                    {ucbDisplay}
                  </span>
                  <span style={{ fontSize: '0.7rem', color: '#8E8270' }}>UCB Weight</span>
                </div>
                <div style={{ fontSize: '0.74rem', color: '#A89E8C', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                  <div>Pulls: <b style={{ color: '#E1DCC9' }}>{arm.pulls}</b></div>
                  <div>Mean Harm: <b style={{ color: '#E1DCC9' }}>{arm.mean_reward.toFixed(2)}</b></div>
                  <div>Breaches: <b style={{ color: arm.win_count > 0 ? '#E63946' : '#2A9D8F' }}>{arm.win_count}</b></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. Vulnerability Fingerprint Table */}
      <div style={{
        backgroundColor: '#1F150C',
        border: '1px solid #412D15',
        borderRadius: '14px',
        padding: '1.5rem',
        marginBottom: '1.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#E1DCC9' }}>
              Target Model Vulnerability Fingerprint Matrix
            </h3>
            <p style={{ fontSize: '0.75rem', color: '#A89E8C' }}>
              Breakdown of susceptibility across adversarial techniques.
            </p>
          </div>
          {fp && (
            <span style={{ fontSize: '0.75rem', color: '#E1DCC9', backgroundColor: '#140D07', padding: '0.3rem 0.6rem', borderRadius: '6px', border: '1px solid #32210F' }}>
              Target: <b style={{ color: '#D97706' }}>{fp.target_model}</b>
            </span>
          )}
        </div>

        {fp ? (
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            textAlign: 'left',
            fontSize: '0.82rem'
          }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #412D15', color: '#A89E8C' }}>
                <th style={{ padding: '0.75rem 0.5rem' }}>Specialist Vector</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Total Probes</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Jailbreaks / Leaks</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Vector ASR (%)</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Mean Harm</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Risk Severity</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(fp.category_breakdown || {}).map(([catId, stats]) => {
                const isHighRisk = stats.win_count > 0 || stats.mean_harm_score >= 0.4;
                return (
                  <tr key={catId} style={{ borderBottom: '1px solid #281A0E', color: '#E1DCC9' }}>
                    <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600 }}>{stats.name}</td>
                    <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'monospace' }}>{stats.pulls}</td>
                    <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'monospace', color: stats.win_count > 0 ? '#E63946' : '#2A9D8F' }}>
                      {stats.win_count}
                    </td>
                    <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'monospace' }}>
                      {(stats.win_rate * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'monospace' }}>
                      {stats.mean_harm_score.toFixed(3)}
                    </td>
                    <td style={{ padding: '0.75rem 0.5rem' }}>
                      <span style={{
                        padding: '0.2rem 0.6rem',
                        borderRadius: '9999px',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        backgroundColor: isHighRisk ? 'rgba(230,57,70,0.2)' : 'rgba(42,157,143,0.2)',
                        color: isHighRisk ? '#FFA5AB' : '#6EE7B7',
                        border: `1px solid ${isHighRisk ? '#E63946' : '#2A9D8F'}`
                      }}>
                        {stats.severity_rating}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#8E8270', fontSize: '0.82rem' }}>
            Launch a red-teaming campaign to synthesize the live vulnerability fingerprint.
          </div>
        )}
      </div>
    </div>
  );
}
