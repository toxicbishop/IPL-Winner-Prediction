import React from 'react';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer
} from 'recharts';
import { ShapFeature } from '../constants/teams';

interface FeatureRadarProps {
  data: ShapFeature[];
  loading: boolean;
}

const FeatureRadar: React.FC<FeatureRadarProps> = ({ data, loading }) => {
  return (
    <div className="card">
      <div className="card-terminal-bar">
        <span className="terminal-id">PROC_ID: SHAP_RADAR</span>
        <span className="terminal-id">FEAT_01-06</span>
      </div>
      <div className="card-body">
        <div className="card-header">
          <h3>Feature Importance</h3>
        </div>
        {loading ? (
          <div className="skeleton" style={{ height: '280px', width: '100%' }} />
        ) : (
          <div style={{ height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="72%" data={data}>
                <PolarGrid
                  stroke="var(--color-border)"
                  strokeDasharray="2 2"
                  gridType="polygon"
                />
                <PolarAngleAxis
                  dataKey="name"
                  tick={{
                    fill: 'var(--color-text-secondary)',
                    fontSize: 9,
                    fontFamily: 'var(--font-mono)',
                    letterSpacing: '0.14em',
                  }}
                />
                <Radar
                  dataKey="val"
                  stroke="var(--color-primary)"
                  fill="var(--color-primary)"
                  fillOpacity={0.18}
                  strokeWidth={1.5}
                  isAnimationActive={true}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeatureRadar;
