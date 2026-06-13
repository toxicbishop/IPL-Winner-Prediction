import React from 'react';
import { NavLink } from 'react-router-dom';
import { Cpu, BarChart3, Brain, LineChart, Settings, Sun, Moon, Trophy, Search, Medal, List, Archive } from 'lucide-react';

interface SidebarProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  onSettingsOpen: () => void;
  theme: 'dark' | 'light';
  onThemeToggle: () => void;
}

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: BarChart3 },
  { id: 'archive', label: 'Archive', icon: Archive },
  { id: 'intelligence', label: 'Intelligence', icon: Brain },
  { id: 'analytics', label: 'Analytics', icon: LineChart },
  { id: 'browse', label: 'Browse Teams', icon: Search },
  { id: 'leaderboard', label: 'Leaderboard', icon: Medal },
  { id: 'visual_insights', label: 'Visual Insights', icon: Trophy },
];

const Sidebar: React.FC<SidebarProps> = ({
  onSettingsOpen, theme, onThemeToggle
}) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand" title="IPL 2027 AI">
        <Cpu size={20} strokeWidth={1.5} />
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(item => {
          let path = '/';
          if (item.id === 'archive') path = '/archive';
          if (item.id === 'intelligence') path = '/intelligence';
          if (item.id === 'analytics') path = '/analytics';
          if (item.id === 'browse') path = '/teams';
          if (item.id === 'leaderboard') path = '/leaderboard';
          if (item.id === 'visual_insights') path = '/insights';

          return (
            <NavLink
              key={item.id}
              to={path}
              className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
              title={item.label}
            >
              <item.icon size={18} strokeWidth={1.5} />
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <button onClick={onThemeToggle} title={theme === 'dark' ? 'Light Mode' : 'Dark Mode'}>
          {theme === 'dark' ? <Sun size={16} strokeWidth={1.5} /> : <Moon size={16} strokeWidth={1.5} />}
        </button>

        <button onClick={onSettingsOpen} title="Settings">
          <Settings size={16} strokeWidth={1.5} />
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
