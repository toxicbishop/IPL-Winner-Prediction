import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useTheme } from "./hooks/useTheme";
import Sidebar from "./components/Sidebar";
import SettingsDrawer from "./components/SettingsDrawer";

import DashboardPage from "./pages/Dashboard";
import TeamsPage from "./pages/TeamsPage";
import TeamDetail from "./pages/TeamDetail";
import PlayersPage from "./pages/PlayersPage";
import PlayerDetail from "./pages/PlayerDetail";
import Simulator from "./pages/Simulator";
import ArchivePage from "./pages/ArchivePage";
import SeasonDetail from "./pages/SeasonDetail";
import AboutPage from "./pages/AboutPage";
import IntelligenceTab from "./components/IntelligenceTab";
import AnalyticsTab from "./components/AnalyticsTab";
import VisualInsights from "./components/VisualInsights";
import LeaderboardTab from "./components/LeaderboardTab";
import { useDashboardData } from "./hooks/useDashboardData";

const queryClient = new QueryClient();

const App: React.FC = () => {
  const [tournament, setTournament] = useState("ipl");
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  // Keep global data fetched for legacy tabs if needed
  const dashboardData = useDashboardData(tournament);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app-layout">
          <Sidebar
            activeTab="overview" // Not strictly needed with router, but keep for compat
            onTabChange={() => {}}
            onSettingsOpen={() => setIsSettingsOpen(true)}
            theme={theme}
            onThemeToggle={toggleTheme}
          />

          <main className="main-content">
            <Routes>
              <Route path="/" element={<DashboardPage dashboardData={dashboardData} />} />

              <Route path="/teams" element={<TeamsPage />} />
              <Route path="/teams/:teamId" element={<TeamDetail />} />
              <Route path="/players" element={<PlayersPage />} />
              <Route path="/players/:playerId" element={<PlayerDetail />} />
              <Route path="/simulator" element={<Simulator />} />
              <Route path="/archive" element={<ArchivePage />} />
              <Route path="/archive/:season" element={<SeasonDetail />} />
              <Route path="/about" element={<AboutPage />} />

              {/* Legacy Tabs migrated to routes */}
              <Route path="/intelligence" element={<IntelligenceTab data={dashboardData.intelligenceData} loading={dashboardData.loading} />} />
              <Route path="/analytics" element={<AnalyticsTab tournament={tournament} />} />
              <Route path="/insights" element={<VisualInsights tournament={tournament} />} />
              <Route path="/leaderboard" element={<LeaderboardTab modelStats={dashboardData.modelStats} loading={dashboardData.loading} />} />
              
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          <SettingsDrawer
            isOpen={isSettingsOpen}
            onClose={() => setIsSettingsOpen(false)}
          />
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
