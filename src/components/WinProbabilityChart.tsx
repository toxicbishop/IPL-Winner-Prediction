import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { TeamData } from '../constants/teams';

interface WinProbabilityChartProps {
  data: TeamData[];
  loading: boolean;
}

const WinProbabilityChart: React.FC<WinProbabilityChartProps> = ({ data, loading }) => {
  return (
    <div className="card">
      <div className="card-terminal-bar">
        <span className="terminal-id">CHART_ID: WIN_PROB_01</span>
        <span className="terminal-id" style={{ color: 'var(--color-primary)' }}>LIVE</span>
      </div>
      <div className="card-body">
        <div className="card-header">
          <h3>Win Probability</h3>
          <span className="mono-label" style={{ fontSize: '0.625rem', color: 'var(--color-text-muted)' }}>
            N={data.length}
          </span>
        </div>
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
            {[...Array(10)].map((_, i) => (
              <div key={i} className="skeleton" style={{ height: '22px', width: '100%' }} />
            ))}
          </div>
        ) : (
          <div style={{ height: '380px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} layout="vertical" margin={{ left: 4, right: 16, top: 4, bottom: 4 }}>
                <XAxis type="number" hide />
                <YAxis
                  dataKey="team" type="category"
                  tick={{
                    fill: 'var(--color-text-secondary)',
                    fontSize: 10,
                    fontFamily: 'var(--font-mono)',
                    letterSpacing: '0.14em',
                  }}
                  axisLine={false} tickLine={false} width={52}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                  contentStyle={{
                    background: 'var(--color-surface)',
                    border: '1px solid var(--color-primary)',
                    borderRadius: 0,
                    fontSize: '0.75rem',
                    fontFamily: 'var(--font-mono)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.14em',
                  }}
                  labelStyle={{
                    color: 'var(--color-text-main)',
                    fontWeight: 600,
                  }}
                  itemStyle={{
                    color: 'var(--color-text-secondary)',
                  }}
                  formatter={(value: number) => [`${value}%`, 'PROB']}
                />
                <Bar dataKey="prob" radius={0} barSize={14}>
                  {data.map((entry, i) => (
                    <Cell key={`cell-${i}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default WinProbabilityChart;
