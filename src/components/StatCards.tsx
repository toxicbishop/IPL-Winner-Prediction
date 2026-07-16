import React from 'react';
import { Zap, Layers, Database, TrendingUp } from 'lucide-react';
import { ModelStat, ShapFeature } from '../constants/teams';

interface StatCardsProps {
  modelStats: ModelStat[];
  shapFeatures: ShapFeature[];
  loading: boolean;
}

const StatCards: React.FC<StatCardsProps> = ({ modelStats, shapFeatures, loading }) => {
  const ensembleAccRaw = modelStats.find(m => m.name === 'ENSEMBLE')?.acc || '0';
  const ensembleAcc = parseFloat(ensembleAccRaw) || 0;
  const topFeature = shapFeatures.length > 0 ? shapFeatures[0].name : '--';

  const cards = [
    {
      id: 'ACC_087',
      icon: Zap,
      value: loading ? '...' : `${ensembleAcc}%`,
      label: 'Ensemble Accuracy',
      accent: 'var(--color-primary)',
      progress: ensembleAcc,
    },
    {
      id: 'MDL_014',
      icon: Layers,
      value: loading ? '...' : `${modelStats.length}`,
      label: 'Models Polled',
      accent: 'var(--color-secondary)',
      progress: Math.min(100, modelStats.length * 10),
    },
    {
      id: 'DAT_1169',
      icon: Database,
      value: '1,169',
      label: 'Matches Analyzed',
      accent: 'var(--color-primary)',
      progress: 100,
    },
    {
      id: 'FEAT_01',
      icon: TrendingUp,
      value: loading ? '...' : topFeature,
      label: 'Top Feature',
      accent: 'var(--color-tertiary)',
      progress: 70,
    },
  ];

  return (
    <div className="stat-cards-row">
      {cards.map(card => (
        <div key={card.label} className="stat-card">
          <div className="card-terminal-bar">
            <span className="terminal-id">METRIC_ID: {card.id}</span>
            <card.icon size={10} strokeWidth={1.5} style={{ color: 'var(--color-text-muted)' }} />
          </div>
          <div className="stat-card-body">
            <div className="stat-card-label">{card.label}</div>
            {loading ? (
              <div className="skeleton" style={{ width: '80px', height: '28px' }} />
            ) : (
              <div className="stat-card-value" style={{ color: card.accent }}>
                {card.value}
              </div>
            )}
            <div className="stat-card-accent-bar">
              <span style={{
                width: `${card.progress}%`,
                background: card.accent,
              }} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatCards;
