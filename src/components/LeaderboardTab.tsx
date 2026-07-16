import React, { useMemo } from 'react';
import { Trophy, TrendingDown, TrendingUp } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { LEADERBOARD_DATA, ModelStat } from '../constants/teams';

interface LeaderboardTabProps {
  modelStats: ModelStat[];
  loading: boolean;
}

const LeaderboardTab: React.FC<LeaderboardTabProps> = ({ modelStats, loading }) => {
  const modelStandings = useMemo(() => {
    const derived = modelStats.map((model, index) => ({
      rank: index + 1,
      model: model.name,
      accuracy: Number(model.acc) || 0,
      auc: model.auc,
      trend: index === 0 ? 3.1 : index === 1 ? 1.4 : -0.3,
    }));
    return derived.length > 0 ? derived.sort((a, b) => b.accuracy - a.accuracy) : [
      { rank: 1, model: 'TEMPORAL XGBOOST', accuracy: 58.2, auc: '0.62', trend: 3.1 },
      { rank: 2, model: 'LIGHTGBM', accuracy: 56.9, auc: '0.60', trend: 1.4 },
      { rank: 3, model: 'ENSEMBLE', accuracy: 55.1, auc: '0.59', trend: -0.3 },
    ];
  }, [modelStats]);

  return (
    <div className="fade-in leaderboard-tab">
      <section className="stat-cards-row">
        <div className="stat-card">
          <div className="card-terminal-bar"><span className="terminal-id">LEADER_ID: USER_01</span><Trophy size={10} /></div>
          <div className="stat-card-body">
            <div className="stat-card-label">Top Predictor</div>
            <div className="stat-card-value" style={{ color: 'var(--color-primary)', fontSize: '2rem' }}>
              {LEADERBOARD_DATA.userStandings[0].name}
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="card-terminal-bar"><span className="terminal-id">POINTS_01</span></div>
          <div className="stat-card-body">
            <div className="stat-card-label">Leader Points</div>
            <div className="stat-card-value">{LEADERBOARD_DATA.userStandings[0].points}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="card-terminal-bar"><span className="terminal-id">MODEL_01</span></div>
          <div className="stat-card-body">
            <div className="stat-card-label">Top Model</div>
            <div className="stat-card-value" style={{ color: 'var(--color-secondary)' }}>
              {loading ? '...' : `${modelStandings[0].accuracy.toFixed(1)}%`}
            </div>
          </div>
        </div>
      </section>

      <section className="leaderboard-grid">
        <div className="card">
          <div className="card-terminal-bar">
            <span className="terminal-id">BOARD_ID: USERS</span>
            <span className="terminal-id">{LEADERBOARD_DATA.updatedAt}</span>
          </div>
          <div className="card-body">
            <div className="card-header"><h3>User Predictions</h3></div>
            <div className="leaderboard-table">
              {LEADERBOARD_DATA.userStandings.map((row) => (
                <div key={row.name} className="leaderboard-row">
                  <span>#{row.rank}</span>
                  <strong>{row.name}</strong>
                  <span>{row.points.toLocaleString()} pts</span>
                  <span>{row.correct} correct</span>
                  <Movement value={row.movement} />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-terminal-bar">
            <span className="terminal-id">BOARD_ID: MODELS</span>
            <span className="terminal-id">CALIBRATED</span>
          </div>
          <div className="card-body">
            <div className="card-header"><h3>Model Standings</h3></div>
            <div style={{ height: 280 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={modelStandings}>
                  <CartesianGrid stroke="var(--color-border)" strokeDasharray="2 2" />
                  <XAxis dataKey="model" tick={{ fill: 'var(--color-text-muted)', fontSize: 9 }} />
                  <YAxis tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ background: 'var(--color-surface)', border: '1px solid var(--color-primary)' }}
                    labelStyle={{ color: 'var(--color-text-main)', fontWeight: 600 }}
                    itemStyle={{ color: 'var(--color-text-secondary)' }}
                  />
                  <Bar dataKey="accuracy" fill="var(--color-primary)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>

      <section className="card">
        <div className="card-terminal-bar">
          <span className="terminal-id">TREND_ID: STANDINGS_OVER_TIME</span>
          <span className="terminal-id">6 WEEK TRACE</span>
        </div>
        <div className="card-body">
          <div className="card-header"><h3>Standings Over Time</h3></div>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={LEADERBOARD_DATA.history}>
                <CartesianGrid stroke="var(--color-border)" strokeDasharray="2 2" />
                <XAxis dataKey="week" tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }} />
                <YAxis tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ background: 'var(--color-surface)', border: '1px solid var(--color-primary)' }}
                  labelStyle={{ color: 'var(--color-text-main)', fontWeight: 600 }}
                  itemStyle={{ color: 'var(--color-text-secondary)' }}
                />
                <Line type="monotone" dataKey="users" stroke="var(--color-primary)" strokeWidth={2} />
                <Line type="monotone" dataKey="models" stroke="var(--color-secondary)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
};

const Movement: React.FC<{ value: number }> = ({ value }) => {
  if (value === 0) return <span className="trend-pill">0</span>;
  const Icon = value > 0 ? TrendingUp : TrendingDown;
  return (
    <span className={`trend-pill ${value > 0 ? 'positive' : 'negative'}`}>
      <Icon size={12} />
      {Math.abs(value)}
    </span>
  );
};

export default LeaderboardTab;
