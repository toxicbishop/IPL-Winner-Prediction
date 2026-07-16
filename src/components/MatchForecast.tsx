import React from 'react';
import { MatchFixture, getTeamLogo } from '../constants/teams';

interface MatchForecastProps {
  schedule: MatchFixture[];
  loading: boolean;
}

const TeamCell: React.FC<{ name: string }> = ({ name }) => {
  const logo = getTeamLogo(name);
  return (
    <span className="flex items-center gap-2">
      {logo && (
        <img
          src={logo}
          alt=""
          aria-hidden="true"
          className="h-5 w-5 shrink-0 object-contain"
          loading="lazy"
        />
      )}
      <span className="mono-label text-xs text-paper">{name}</span>
    </span>
  );
};

const MatchForecast: React.FC<MatchForecastProps> = ({ schedule, loading }) => {
  return (
    <div className="card">
      <div className="card-terminal-bar">
        <span className="terminal-id">SCHED_ID: FIXT_UPCOMING</span>
        <span className="terminal-id" style={{ color: 'var(--color-secondary)' }}>
          {schedule.length} SLOTS
        </span>
      </div>
      <div className="card-body">
        <div className="card-header">
          <h3>Match Forecast</h3>
        </div>

        <div className="data-table">
          <div
            className="table-header"
            style={{ gridTemplateColumns: '1fr 1.5fr 1.5fr 1.25fr' }}
          >
            <span>Date</span>
            <span>Home</span>
            <span>Away</span>
            <span>Predicted Winner</span>
          </div>

          {loading ? (
            <div className="flex flex-col gap-2 pt-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="skeleton h-10" />
              ))}
            </div>
          ) : (
            <div>
              {schedule.map((match, i) => {
                const winnerLogo = getTeamLogo(match.predicted_winner);
                return (
                  <div
                    key={i}
                    className="table-row"
                    style={{ gridTemplateColumns: '1fr 1.5fr 1.5fr 1.25fr' }}
                  >
                    <span className="mono-label text-[0.6875rem] text-paper-muted">
                      {match.date || 'TBD'}
                    </span>
                    <TeamCell name={match.team1} />
                    <TeamCell name={match.team2} />
                    <div className="flex items-center gap-2">
                      {winnerLogo ? (
                        <img
                          src={winnerLogo}
                          alt=""
                          aria-hidden="true"
                          className="h-5 w-5 shrink-0 object-contain"
                          loading="lazy"
                        />
                      ) : (
                        <span className="h-1.5 w-1.5 shrink-0 bg-saffron" />
                      )}
                      <span className="mono-label text-xs font-bold text-saffron">
                        {match.predicted_winner}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MatchForecast;
