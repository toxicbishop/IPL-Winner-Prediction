import React from 'react';

interface VisualInsightsProps {
  tournament: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const VisualInsights: React.FC<VisualInsightsProps> = ({ tournament }) => {
  const images = React.useMemo(() => [
    { title: 'Win Probability Breakdown', path: `${API_BASE}/outputs/results/${tournament}/win_probability.png?v=${Date.now()}`, desc: 'Probability distribution across the 2027 tournament cycle.' },
    { title: 'Feature Intelligence (Why)', path: `${API_BASE}/outputs/results/${tournament}/shap_summary_lightgbm.png?v=${Date.now()}`, desc: 'Detailed breakdown of heuristic signals driving team rankings.' },
    { title: 'Match Forecast Model', path: `${API_BASE}/outputs/results/${tournament}/model_comparison.png?v=${Date.now()}`, desc: 'Upcoming fixture simulations and venue-specific outcomes.' }
  ], [tournament]);

  return (
    <div className="fade-in space-y-8">
      <div className="card">
        <div className="card-terminal-bar">
          <span className="terminal-id">VISUAL_ID: SYSTEM_SNAPSHOTS</span>
          <span className="terminal-id">GRAPH_CORE</span>
        </div>
        <div className="card-body">
          <div className="card-header">
            <h3>Analytical Snapshots</h3>
          </div>
          <p className="text-sm text-paper-muted mb-6">
            Static visual breakdowns of the core model logic and tournament simulations.
          </p>

          <div className="grid grid-cols-1 gap-12">
            {images.map((img, i) => (
              <div key={i} className="space-y-4">
                <h4 className="font-mono text-xs uppercase tracking-widest text-paper-muted border-l-2 border-paper-accent pl-3">
                  {img.title}
                </h4>
                <div className="bg-paper-darker p-4 border border-paper-muted/10 rounded-lg">
                  <img 
                    src={img.path} 
                    alt={img.title} 
                    className="w-full h-auto rounded shadow-2xl" 
                  />
                </div>
                <p className="text-xs italic text-paper-muted/80 pl-2">
                  {img.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualInsights;
