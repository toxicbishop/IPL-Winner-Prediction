import React from 'react';
import { Trophy, Star } from 'lucide-react';
import { TeamData, getTeamLogo } from '../constants/teams';

interface HeroChampionProps {
  topTeam: TeamData | null;
  loading: boolean;
}

const HeroChampion: React.FC<HeroChampionProps> = ({ topTeam, loading }) => {
  if (loading) {
    return (
      <div className="hero-champion">
        <div className="skeleton h-24 w-24" />
        <div className="flex flex-1 flex-col gap-2">
          <div className="skeleton h-3.5 w-44" />
          <div className="skeleton h-8 w-80" />
          <div className="skeleton h-3.5 w-[420px] max-w-full" />
        </div>
        <div className="skeleton h-14 w-36" />
      </div>
    );
  }

  if (!topTeam) return null;

  const logo = getTeamLogo(topTeam.team);
  const trend = topTeam.trend || 0;
  const confidence = topTeam.confidence || 'Medium';

  return (
    <div
      className="hero-champion"
      style={{ borderTop: `2px solid ${topTeam.color}` }}
    >
      <div
        className="hero-champion-icon"
        style={{ color: topTeam.color, borderColor: topTeam.color }}
      >
        {logo ? (
          <img
            src={logo}
            alt={`${topTeam.team} logo`}
            className="max-h-[80%] max-w-[80%] object-contain"
            loading="eager"
          />
        ) : (
          <Trophy size={40} strokeWidth={1.25} />
        )}
      </div>

      <div className="hero-champion-info">
        <span className="eyebrow flex items-center gap-2">
          <span className="flex items-center">
            <Star size={10} className="mr-1 inline -translate-y-px" />
            Predicted Champion
          </span>
          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase ${
            confidence === 'High' ? 'bg-green-500/20 text-green-400' : 
            confidence === 'Medium' ? 'bg-blue-500/20 text-blue-400' : 'bg-orange-500/20 text-orange-400'
          }`}>
            {confidence} Confidence
          </span>
        </span>
        <div className="flex items-baseline gap-4">
          <h2>{topTeam.team}</h2>
          {trend !== 0 && (
            <span className={`text-sm font-bold ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
            </span>
          )}
        </div>
        <p>
          Driven by {topTeam.explanation?.why[0] || 'squad stability'} and recent {topTeam.explanation?.why[1] || 'performance'} signals.
        </p>
      </div>

      <div className="flex flex-col items-end">
        <div className="hero-prob-badge">
          {topTeam.prob}
          <span className="ml-1 font-mono text-xl tracking-mono text-paper-muted">%</span>
        </div>
        <div className="hero-prob-badge-label">Win Probability</div>
      </div>
    </div>
  );
};

export default HeroChampion;
