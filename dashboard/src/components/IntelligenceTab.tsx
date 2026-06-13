import React, { useState, useEffect } from 'react';
import { IntelligenceData, TEAM_COLORS } from '../constants/teams';

interface IntelligenceTabProps {
  data: IntelligenceData | null;
  loading: boolean;
}

const IntelligenceTab: React.FC<IntelligenceTabProps> = ({ data, loading }) => {
  const teamKeys = Object.keys(TEAM_COLORS).slice(0, 10);

  const [team1, setTeam1] = useState("CSK");
  const [team2, setTeam2] = useState("MI");
  const [prob, setProb] = useState<number | null>(null);
  const [loadingSim, setLoadingSim] = useState(false);

  useEffect(() => {
    if (team1 === team2) {
      setProb(50.0);
      return;
    }

    setLoadingSim(true);
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

    fetch(`${API_BASE}/simulate-h2h?team1=${team1}&team2=${team2}`)
      .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then(res => {
        setProb(res.team1_win_prob);
        setLoadingSim(false);
      })
      .catch(() => {
        // Fallback squad strength comparison math
        if (data && data.squad_strength) {
          const s1 = data.squad_strength[team1] || 7.0;
          const s2 = data.squad_strength[team2] || 7.0;
          const calculated = Math.round((s1 / (s1 + s2)) * 1000) / 10;
          setProb(calculated);
        } else {
          setProb(50.0);
        }
        setLoadingSim(false);
      });
  }, [team1, team2, data]);

  const team1Prob = prob !== null ? prob : 50.0;
  const team2Prob = 100 - team1Prob;
  const predictedWinner = team1Prob >= 50.0 ? team1 : team2;

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      <div className="card">
        <div className="card-terminal-bar">
          <span className="terminal-id">INTEL_ID: BAYES_H2H</span>
          <span className="terminal-id">DUAL_PANEL</span>
        </div>
        <div
          className="card-body"
          style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, padding: 0 }}
        >
          {/* Bayesian Priors */}
          <div style={{ padding: 'var(--space-lg)', borderRight: '1px solid var(--color-border)' }}>
            <div className="card-header">
              <h3>Bayesian Squad Priors</h3>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-lg)' }}>
              Raw mathematical anchors reflecting 2027 auction strengths and historical playoff frequency.
            </p>

            {loading || !data ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="skeleton" style={{ height: '28px' }} />
                ))}
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                {Object.entries(data.squad_strength)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 8)
                  .map(([team, val]) => (
                    <div key={team}>
                      <div style={{
                        display: 'flex', justifyContent: 'space-between',
                        fontSize: '0.75rem', marginBottom: '6px',
                        fontFamily: 'var(--font-mono)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                      }}>
                        <span style={{ fontWeight: 600, color: TEAM_COLORS[team] || 'var(--color-text-main)' }}>
                          {team}
                        </span>
                        <span style={{ color: 'var(--color-text-muted)' }}>
                          {val}/10
                        </span>
                      </div>
                      <div className="progress-bar">
                        <div
                          className="progress-bar-fill"
                          style={{
                            width: `${(val / 10) * 100}%`,
                            background: TEAM_COLORS[team] || 'var(--color-primary)',
                          }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>

          {/* Head-to-Head Simulator */}
          <div style={{ padding: 'var(--space-lg)', background: 'var(--color-surface-alt)' }}>
            <div className="card-header">
              <h3>Head-to-Head Simulator</h3>
            </div>

            <div style={{ display: 'flex', gap: 'var(--space-sm)', marginBottom: 'var(--space-xl)', alignItems: 'center' }}>
              <select
                className="form-select"
                style={{ flex: 1 }}
                value={team1}
                onChange={(e) => setTeam1(e.target.value)}
              >
                {teamKeys.filter(t => t !== team2).map(t => <option key={t}>{t}</option>)}
              </select>
              <span
                className="mono-label"
                style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}
              >
                VS
              </span>
              <select
                className="form-select"
                style={{ flex: 1 }}
                value={team2}
                onChange={(e) => setTeam2(e.target.value)}
              >
                {teamKeys.filter(t => t !== team1).map(t => <option key={t}>{t}</option>)}
              </select>
            </div>

            <div style={{
              textAlign: 'center',
              padding: 'var(--space-lg) var(--space-md)',
              border: '1px solid var(--color-border)',
              background: 'var(--color-bg)',
              position: 'relative',
              borderRadius: '6px',
            }}>
              {loadingSim && (
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'rgba(0,0,0,0.5)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--color-text-muted)',
                  borderRadius: '6px',
                  zIndex: 10,
                }}>
                  SIMULATING...
                </div>
              )}

              {/* Projected Winner Accent Box */}
              <div style={{
                display: 'inline-block',
                padding: '6px 12px',
                background: 'var(--color-surface)',
                border: `1px solid ${TEAM_COLORS[predictedWinner] || 'var(--color-border)'}`,
                borderRadius: '4px',
                color: TEAM_COLORS[predictedWinner] || 'var(--color-text-main)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.7rem',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                marginBottom: 'var(--space-lg)',
                fontWeight: 700,
              }}>
                PROJECTED WINNER: {predictedWinner === team1 ? `${team1} (${team1Prob.toFixed(1)}%)` : `${team2} (${team2Prob.toFixed(1)}%)`}
              </div>

              {/* Large Split Probabilities display */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: 'var(--space-md)',
                padding: '0 var(--space-xs)',
              }}>
                {/* Team 1 Prob */}
                <div style={{ textAlign: 'left' }}>
                  <div style={{
                    fontSize: '1.75rem',
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)',
                    color: TEAM_COLORS[team1] || 'var(--color-text-main)',
                    letterSpacing: '-0.02em',
                  }}>
                    {team1Prob.toFixed(1)}<span style={{ fontSize: '1rem', color: 'var(--color-text-muted)', fontWeight: 400 }}>%</span>
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.65rem',
                    color: 'var(--color-text-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}>
                    {team1} PROBABILITY
                  </div>
                </div>

                {/* VS accent text */}
                <div style={{
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--color-text-muted)',
                  fontWeight: 600,
                  opacity: 0.5,
                }}>
                  VS
                </div>

                {/* Team 2 Prob */}
                <div style={{ textAlign: 'right' }}>
                  <div style={{
                    fontSize: '1.75rem',
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)',
                    color: TEAM_COLORS[team2] || 'var(--color-text-main)',
                    letterSpacing: '-0.02em',
                  }}>
                    {team2Prob.toFixed(1)}<span style={{ fontSize: '1rem', color: 'var(--color-text-muted)', fontWeight: 400 }}>%</span>
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.65rem',
                    color: 'var(--color-text-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}>
                    {team2} PROBABILITY
                  </div>
                </div>
              </div>

              {/* Dual-colored visual split bar */}
              <div style={{
                display: 'flex',
                height: '6px',
                borderRadius: '3px',
                overflow: 'hidden',
                background: 'var(--color-surface-highest)',
                marginBottom: 'var(--space-xs)',
              }}>
                <div style={{
                  width: `${team1Prob}%`,
                  background: TEAM_COLORS[team1] || 'var(--color-primary)',
                  transition: 'width 0.3s ease',
                }} />
                <div style={{
                  width: `${team2Prob}%`,
                  background: TEAM_COLORS[team2] || 'var(--color-secondary)',
                  transition: 'width 0.3s ease',
                }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Form / Playoff Rate */}
      {data && (
        <div className="card">
          <div className="card-terminal-bar">
            <span className="terminal-id">INTEL_ID: FORM_PLAYOFF</span>
            <span className="terminal-id">WINDOW_3Y</span>
          </div>
          <div
            className="card-body"
            style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0, padding: 0 }}
          >
            <div style={{ padding: 'var(--space-lg)', borderRight: '1px solid var(--color-border)' }}>
              <div className="card-header">
                <h3>Playoff Conversion Rate (3-yr)</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                {Object.entries(data.playoff_rate)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 6)
                  .map(([team, val]) => (
                    <div
                      key={team}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: 'var(--space-sm) 0',
                        borderBottom: '1px solid var(--color-surface-highest)',
                        fontFamily: 'var(--font-mono)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        fontSize: '0.75rem',
                      }}
                    >
                      <span style={{ fontWeight: 600 }}>{team}</span>
                      <span style={{ color: 'var(--color-secondary)' }}>
                        {(val * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
              </div>
            </div>
            <div style={{ padding: 'var(--space-lg)' }}>
              <div className="card-header">
                <h3>2025 Season Form Score</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                {Object.entries(data.form_score)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 6)
                  .map(([team, val]) => (
                    <div
                      key={team}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: 'var(--space-sm) 0',
                        borderBottom: '1px solid var(--color-surface-highest)',
                        fontFamily: 'var(--font-mono)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        fontSize: '0.75rem',
                      }}
                    >
                      <span style={{ fontWeight: 600 }}>{team}</span>
                      <span style={{ color: 'var(--color-primary)' }}>
                        {val.toFixed(2)}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntelligenceTab;
