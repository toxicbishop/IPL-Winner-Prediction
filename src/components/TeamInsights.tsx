import React from 'react';
import { CheckCircle2, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { TeamData } from '../constants/teams';

interface TeamInsightsProps {
  teams: TeamData[];
  loading: boolean;
}

const TeamInsights: React.FC<TeamInsightsProps> = ({ teams, loading }) => {
  if (loading) return <div className="skeleton h-64 w-full" />;
  
  return (
    <div className="card mt-6">
      <div className="card-terminal-bar">
        <span className="terminal-id">INSIGHT_ID: TEAM_QUALITATIVE_BREAKDOWN</span>
        <span className="terminal-id">LIVE_SIGNALS</span>
      </div>
      <div className="card-body">
        <div className="card-header">
          <h3>Why they are winning (or losing)</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
          {teams.slice(0, 6).map((team) => (
            <div key={team.team} className="p-4 border border-paper-muted/20 rounded bg-paper-darker/30">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: team.color }} 
                  />
                  <span className="font-bold font-mono">{team.team}</span>
                </div>
                {team.trend !== 0 && (
                  <div className={`flex items-center text-[10px] font-bold ${team.trend! > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {team.trend! > 0 ? <TrendingUp size={12} className="mr-1" /> : <TrendingDown size={12} className="mr-1" />}
                    {Math.abs(team.trend!)}%
                  </div>
                )}
              </div>

              <div className="space-y-2">
                {team.explanation?.why.map((reason, i) => (
                  <div key={i} className="flex items-start gap-2 text-[11px] text-paper-muted">
                    <CheckCircle2 size={12} className="text-green-500 mt-0.5 shrink-0" />
                    <span>{reason}</span>
                  </div>
                ))}
                {team.explanation?.risk.map((risk, i) => (
                  <div key={i} className="flex items-start gap-2 text-[11px] text-paper-muted">
                    <AlertTriangle size={12} className="text-orange-500 mt-0.5 shrink-0" />
                    <span>{risk}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TeamInsights;
