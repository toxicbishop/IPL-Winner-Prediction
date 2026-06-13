import React, { useState } from 'react';

interface AnalyticsTabProps {
  tournament: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/** Renders an analytics chart image with a graceful fallback if the backend is unreachable. */
const ChartImage: React.FC<{ src: string; alt: string }> = ({ src, alt }) => {
  const [failed, setFailed] = useState(false);

  if (!API_BASE || failed) {
    return (
      <div style={{
        padding: 'var(--space-xl)',
        textAlign: 'center',
        color: 'var(--color-text-muted)',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.75rem',
        border: '1px dashed var(--color-border)',
        background: 'var(--color-bg)',
        letterSpacing: '0.05em',
        textTransform: 'uppercase',
      }}>
        Chart unavailable — backend offline
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      onError={() => setFailed(true)}
      style={{
        maxWidth: '100%',
        height: 'auto',
        maxHeight: '500px',
        display: 'block',
        filter: 'var(--img-invert)',
      }}
    />
  );
};

const AnalyticsTab: React.FC<AnalyticsTabProps> = ({ tournament }) => {
  const cacheBuster = React.useMemo(() => Date.now(), [tournament]);

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2xl)' }}>
      {/* Historical Context */}
      <div>
        <div className="card">
          <div className="card-terminal-bar">
            <span className="terminal-id">ANAL_ID: HIST_WIN_RATE</span>
            <span className="terminal-id">2008-PRESENT</span>
          </div>
          <div className="card-body">
            <div className="card-header">
              <h3>Historical Win-Rate Timeline</h3>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-lg)' }}>
              Aggregated win rates mapping franchise dominance from 2008 to present day.
            </p>
            <div style={{
              padding: 'var(--space-md)',
              display: 'flex',
              justifyContent: 'center',
              background: 'var(--color-bg)',
              border: '1px solid var(--color-surface-highest)',
            }}>
              <ChartImage
                src={`${API_BASE}/outputs/results/${tournament}/historical_win_rates.png?v=${cacheBuster}`}
                alt="Historical Win Rates"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Model Comparison + SHAP */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)' }}>
        <div className="card">
          <div className="card-terminal-bar">
            <span className="terminal-id">ANAL_ID: VENUE_MATRIX</span>
            <span className="terminal-id">XREF</span>
          </div>
          <div className="card-body">
            <div className="card-header">
              <h3>Venue / Toss Matrix</h3>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-lg)' }}>
              Cross-referencing toss decision impact across tournament venues.
            </p>
            <div style={{
              padding: 'var(--space-md)',
              background: 'var(--color-bg)',
              border: '1px solid var(--color-surface-highest)',
            }}>
              <ChartImage
                src={`${API_BASE}/outputs/results/${tournament}/model_comparison.png?v=${cacheBuster}`}
                alt="Model Comparison"
              />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-terminal-bar">
            <span className="terminal-id">ANAL_ID: MODEL_PERF</span>
            <span className="terminal-id">EVAL</span>
          </div>
          <div className="card-body">
            <div className="card-header">
              <h3>Ensemble Model Performance</h3>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-lg)' }}>
              Comparative breakdown of Logistic Regression, Extra Trees, and LightGBM models.
            </p>
            <div style={{
              padding: 'var(--space-md)',
              background: 'var(--color-bg)',
              border: '1px solid var(--color-surface-highest)',
            }}>
              <ChartImage
                src={`${API_BASE}/outputs/results/${tournament}/shap_summary_lightgbm.png?v=${cacheBuster}`}
                alt="SHAP Summary (LightGBM)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsTab;
