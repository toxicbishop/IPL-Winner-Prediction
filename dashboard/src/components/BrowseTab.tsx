import React, { useMemo, useState } from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';
import { PLAYER_DIRECTORY, PlayerData, TeamData, getTeamLogo } from '../constants/teams';
import { ErrorBanner, WidgetSkeleton } from './ApiState';

interface BrowseTabProps {
  teams: TeamData[];
  loading: boolean;
  error?: string | null;
  onRetry: () => void;
}

const ROLES = ['ANY', 'BAT', 'BOWL', 'ALL', 'WK'] as const;
const CONFIDENCE = ['ALL', 'High', 'Medium', 'Low'] as const;

const BrowseTab: React.FC<BrowseTabProps> = ({ teams, loading, error, onRetry }) => {
  const [teamSearch, setTeamSearch] = useState('');
  const [teamConfidence, setTeamConfidence] = useState('ALL');
  const [teamSort, setTeamSort] = useState('prob');
  const [playerSearch, setPlayerSearch] = useState('');
  const [playerRole, setPlayerRole] = useState('ANY');
  const [playerTeam, setPlayerTeam] = useState('ALL');
  const [playerSort, setPlayerSort] = useState('impact');

  const filteredTeams = useMemo(() => {
    const needle = teamSearch.trim().toLowerCase();
    return [...teams]
      .filter((team) => {
        if (needle && !team.team.toLowerCase().includes(needle)) return false;
        if (teamConfidence !== 'ALL' && team.confidence !== teamConfidence) return false;
        return true;
      })
      .sort((a, b) => {
        if (teamSort === 'trend') return (b.trend || 0) - (a.trend || 0);
        if (teamSort === 'confidence') return String(a.confidence).localeCompare(String(b.confidence));
        return b.prob - a.prob;
      });
  }, [teamConfidence, teamSearch, teamSort, teams]);

  const playerTeams = useMemo(() => ['ALL', ...Array.from(new Set(PLAYER_DIRECTORY.map((p) => p.team))).sort()], []);

  const filteredPlayers = useMemo(() => {
    const needle = playerSearch.trim().toLowerCase();
    return [...PLAYER_DIRECTORY]
      .filter((player) => {
        if (playerRole !== 'ANY' && player.role !== playerRole) return false;
        if (playerTeam !== 'ALL' && player.team !== playerTeam) return false;
        if (needle && !`${player.name} ${player.team} ${player.role} ${player.nationality}`.toLowerCase().includes(needle)) return false;
        return true;
      })
      .sort((a, b) => {
        if (playerSort === 'form') return b.form - a.form;
        if (playerSort === 'name') return a.name.localeCompare(b.name);
        if (playerSort === 'team') return a.team.localeCompare(b.team) || b.impact - a.impact;
        return b.impact - a.impact;
      });
  }, [playerRole, playerSearch, playerSort, playerTeam]);

  return (
    <div className="fade-in browse-tab">
      {error && <ErrorBanner message={error} onRetry={onRetry} />}

      <section className="card">
        <div className="card-terminal-bar">
          <span className="terminal-id">BROWSE_ID: TEAMS</span>
          <span className="terminal-id">{filteredTeams.length} ROWS</span>
        </div>
        <div className="card-body">
          <div className="card-header">
            <h3>Teams</h3>
          </div>
          <div className="filter-row">
            <SearchBox value={teamSearch} onChange={setTeamSearch} placeholder="Search team" />
            <Segmented value={teamConfidence} options={CONFIDENCE} onChange={setTeamConfidence} />
            <SortSelect value={teamSort} onChange={setTeamSort} options={[
              ['prob', 'Win probability'],
              ['trend', 'Trend'],
              ['confidence', 'Confidence'],
            ]} />
          </div>

          {loading ? <WidgetSkeleton rows={6} /> : (
            <div className="browse-grid">
              {filteredTeams.map((team) => <TeamCard key={team.team} team={team} />)}
            </div>
          )}
        </div>
      </section>

      <section className="card">
        <div className="card-terminal-bar">
          <span className="terminal-id">BROWSE_ID: PLAYERS</span>
          <span className="terminal-id">{filteredPlayers.length} ROWS</span>
        </div>
        <div className="card-body">
          <div className="card-header">
            <h3>Players</h3>
          </div>
          <div className="filter-row">
            <SearchBox value={playerSearch} onChange={setPlayerSearch} placeholder="Search player, team, country" />
            <Segmented value={playerRole} options={ROLES} onChange={setPlayerRole} />
            <SortSelect value={playerTeam} onChange={setPlayerTeam} options={playerTeams.map((team) => [team, team === 'ALL' ? 'All teams' : team])} />
            <SortSelect value={playerSort} onChange={setPlayerSort} options={[
              ['impact', 'Impact'],
              ['form', 'Form'],
              ['team', 'Team'],
              ['name', 'Name'],
            ]} />
          </div>

          <div className="browse-grid player-grid">
            {filteredPlayers.map((player) => <PlayerCard key={player.id} player={player} />)}
          </div>
        </div>
      </section>
    </div>
  );
};

const SearchBox: React.FC<{ value: string; onChange: (value: string) => void; placeholder: string }> = ({ value, onChange, placeholder }) => (
  <label className="filter-search">
    <Search size={15} strokeWidth={1.5} />
    <input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} />
  </label>
);

const Segmented: React.FC<{ value: string; options: readonly string[]; onChange: (value: string) => void }> = ({ value, options, onChange }) => (
  <div className="segmented-control">
    {options.map((option) => (
      <button key={option} className={value === option ? 'active' : ''} onClick={() => onChange(option)}>
        {option === 'ANY' ? 'ALL' : option}
      </button>
    ))}
  </div>
);

const SortSelect: React.FC<{ value: string; onChange: (value: string) => void; options: string[][] }> = ({ value, onChange, options }) => (
  <label className="filter-select">
    <SlidersHorizontal size={15} strokeWidth={1.5} />
    <select value={value} onChange={(event) => onChange(event.target.value)}>
      {options.map(([option, label]) => <option key={option} value={option}>{label}</option>)}
    </select>
  </label>
);

const TeamCard: React.FC<{ team: TeamData }> = ({ team }) => {
  const logo = getTeamLogo(team.team);
  return (
    <article className="browse-card">
      <div className="browse-card-head">
        <div className="team-mark" style={{ background: team.color }}>
          {logo ? <img src={logo} alt="" aria-hidden="true" /> : team.team}
        </div>
        <div>
          <h4>{team.team}</h4>
          <p>{team.confidence || 'Signal'} confidence</p>
        </div>
      </div>
      <div className="browse-metric-row">
        <span>Win Prob</span>
        <strong>{team.prob.toFixed(2)}%</strong>
      </div>
      <div className="progress-bar"><div className="progress-bar-fill" style={{ width: `${team.prob}%`, background: team.color }} /></div>
      <div className={`trend-pill ${(team.trend || 0) >= 0 ? 'positive' : 'negative'}`}>
        {(team.trend || 0) >= 0 ? '+' : ''}{team.trend || 0} trend
      </div>
    </article>
  );
};

const PlayerCard: React.FC<{ player: PlayerData }> = ({ player }) => (
  <article className="browse-card">
    <div className="browse-card-head">
      <div className="team-mark compact">{player.team}</div>
      <div>
        <h4>{player.name}</h4>
        <p>{player.role} / {player.nationality}</p>
      </div>
    </div>
    <div className="player-metrics">
      <div><span>Form</span><strong>{player.form}</strong></div>
      <div><span>Impact</span><strong>{player.impact}</strong></div>
    </div>
  </article>
);

export default BrowseTab;
