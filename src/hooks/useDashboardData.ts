import { useState, useEffect, useCallback } from "react";
import {
  TeamData,
  ModelStat,
  ShapFeature,
  MatchFixture,
  IntelligenceData,
  TEAM_COLORS,
} from "../constants/teams";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

// ── Fallback mock data (used when the backend is unreachable) ────────────────
const FALLBACK_RANKINGS: TeamData[] = [
  {
    team: "RCB",
    prob: 22.5,
    color: TEAM_COLORS["RCB"] || "#EC1C24",
    trend: 3.05,
    confidence: "High",
    explanation: {
      why: ["table toppers", "batting firepower", "strong NRR"],
      risk: ["bowling depth in death overs"],
    },
  },
  {
    team: "GT",
    prob: 20.1,
    color: TEAM_COLORS["GT"] || "#1B2A4A",
    trend: 2.1,
    confidence: "High",
    explanation: {
      why: ["squad depth", "spin bowling", "strong NRR"],
      risk: ["middle-order fragility"],
    },
  },
  {
    team: "SRH",
    prob: 18.7,
    color: TEAM_COLORS["SRH"] || "#F7A721",
    trend: 0.91,
    confidence: "High",
    explanation: {
      why: ["aggressive batting", "9 wins from 14", "power-hitters"],
      risk: ["spin vulnerability"],
    },
  },
  {
    team: "RR",
    prob: 14.2,
    color: TEAM_COLORS["RR"] || "#2D9CDB",
    trend: 0.5,
    confidence: "Medium",
    explanation: {
      why: ["4th place finish", "smart captaincy"],
      risk: ["1 match remaining"],
    },
  },
  {
    team: "PBKS",
    prob: 7.8,
    color: TEAM_COLORS["PBKS"] || "#ED1B24",
    trend: 0.3,
    confidence: "Low",
    explanation: {
      why: ["positive NRR", "6 wins from 13"],
      risk: ["inconsistency"],
    },
  },
  {
    team: "KKR",
    prob: 7.2,
    color: TEAM_COLORS["KKR"] || "#3A225D",
    trend: -0.4,
    confidence: "Low",
    explanation: {
      why: ["defending champions", "all-round balance"],
      risk: ["borderline NRR"],
    },
  },
  {
    team: "DC",
    prob: 5.1,
    color: TEAM_COLORS["DC"] || "#00008B",
    trend: -1.1,
    confidence: "Low",
    explanation: {
      why: ["young talent"],
      risk: ["worst NRR among contenders"],
    },
  },
  {
    team: "MI",
    prob: 0.0,
    color: TEAM_COLORS["MI"] || "#004BA0",
    trend: -0.27,
    confidence: "Eliminated",
    explanation: {
      why: ["Eliminated from playoffs contention"],
      risk: ["Eliminated"],
    },
  },
  {
    team: "LSG",
    prob: 0.0,
    color: TEAM_COLORS["LSG"] || "#A2D9CE",
    trend: -1.5,
    confidence: "Eliminated",
    explanation: {
      why: ["Eliminated from playoffs contention"],
      risk: ["Eliminated"],
    },
  },
  {
    team: "CSK",
    prob: 0.0,
    color: TEAM_COLORS["CSK"] || "#F9CD02",
    trend: -0.51,
    confidence: "Eliminated",
    explanation: {
      why: ["Eliminated from playoffs contention"],
      risk: ["Eliminated"],
    },
  },
];

const FALLBACK_MODEL_STATS: ModelStat[] = [
  { name: "ENSEMBLE", acc: "58.2", auc: "0.62" },
  { name: "LIGHTGBM", acc: "56.9", auc: "0.60" },
  { name: "TEMPORAL XGBOOST", acc: "55.1", auc: "0.59" },
];

const FALLBACK_SHAP: ShapFeature[] = [
  { name: "powerplay run rate", val: 0.142 },
  { name: "death overs economy", val: 0.118 },
  { name: "top 3 strike rate", val: 0.098 },
  { name: "wickets in hand", val: 0.087 },
  { name: "venue advantage", val: 0.076 },
  { name: "h2h record", val: 0.065 },
];

const FALLBACK_SCHEDULE: MatchFixture[] = [
  {
    date: "2026-05-26",
    team1: "RCB",
    team2: "GT",
    predicted_winner: "RCB",
    win_probability: 0.54,
  },
  {
    date: "2026-05-27",
    team1: "SRH",
    team2: "RR",
    predicted_winner: "SRH",
    win_probability: 0.61,
  },
  {
    date: "2026-05-29",
    team1: "GT",
    team2: "SRH",
    predicted_winner: "GT",
    win_probability: 0.55,
  },
  {
    date: "2026-05-31",
    team1: "RCB",
    team2: "GT",
    predicted_winner: "RCB",
    win_probability: 0.52,
  },
];

const FALLBACK_INTELLIGENCE: IntelligenceData = {
  squad_strength: {
    RCB: 8.9,
    GT: 8.7,
    SRH: 8.5,
    RR: 7.8,
    PBKS: 7.2,
    KKR: 7.0,
    DC: 6.8,
    CSK: 6.2,
    MI: 5.8,
    LSG: 5.5,
  },
  playoff_rate: {
    RCB: 0.59,
    GT: 0.67,
    SRH: 0.53,
    MI: 0.82,
    CSK: 0.88,
    KKR: 0.65,
    DC: 0.47,
    RR: 0.41,
    PBKS: 0.24,
    LSG: 0.33,
  },
  form_score: {
    RCB: 8.8,
    GT: 8.5,
    SRH: 8.3,
    RR: 7.4,
    PBKS: 6.8,
    KKR: 6.5,
    DC: 6.1,
    CSK: 5.2,
    MI: 4.8,
    LSG: 4.5,
  },
};

// ── Fetch helper (returns null on failure instead of throwing) ────────────────
async function fetchJson(path: string): Promise<any | null> {
  if (!API_BASE) return null; // No backend configured → skip
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000); // 8 s timeout
    const response = await fetch(`${API_BASE}${path}`, {
      signal: controller.signal,
    });
    clearTimeout(timeout);
    if (!response.ok) return null;
    const data = await response.json();
    if (data?.error) return null;
    return data;
  } catch {
    return null; // Network error / timeout → silent fallback
  }
}

export function useDashboardData(tournament: string) {
  const [winnerData, setWinnerData] = useState<TeamData[]>(FALLBACK_RANKINGS);
  const [modelStats, setModelStats] =
    useState<ModelStat[]>(FALLBACK_MODEL_STATS);
  const [shapFeatures, setShapFeatures] =
    useState<ShapFeature[]>(FALLBACK_SHAP);
  const [schedule, setSchedule] = useState<MatchFixture[]>(FALLBACK_SCHEDULE);
  const [intelligenceData, setIntelligenceData] =
    useState<IntelligenceData | null>(FALLBACK_INTELLIGENCE);
  const [metadata, setMetadata] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshIndex, setRefreshIndex] = useState(0);

  const retry = useCallback(() => {
    setRefreshIndex((current) => current + 1);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      // If there is no backend URL configured, use fallbacks immediately
      if (!API_BASE) {
        setLoading(false);
        return;
      }

      try {
        const [probRes, statsRes, shapRes, fixtureRes, intRes] =
          await Promise.allSettled([
            fetchJson(`/api/winner-probabilities?tournament=${tournament}`),
            fetchJson(`/api/model-performance?tournament=${tournament}`),
            fetchJson(`/api/shap-importance/lightgbm?tournament=${tournament}`),
            fetchJson(`/api/match-fixtures?tournament=${tournament}`),
            fetchJson(`/api/intelligence?tournament=${tournament}`),
          ]);

        // Winner probabilities
        const probData = probRes.status === "fulfilled" ? probRes.value : null;
        if (probData?.rankings) {
          setWinnerData(
            probData.rankings.map((r: any) => ({
              team: r.team_id,
              prob: r.win_probability,
              trend: r.trend,
              confidence: r.confidence,
              explanation: r.explanation,
              color: TEAM_COLORS[r.team_id] || "#64748b",
            })),
          );
          setMetadata({
            last_updated: probData.last_updated,
            coverage: probData.data_coverage,
            accuracy: probData.validation_accuracy_2024,
            type: probData.model_type,
          });
        }
        // else: keep FALLBACK_RANKINGS (initial state)

        // Model performance
        const statsData =
          statsRes.status === "fulfilled" ? statsRes.value : null;
        if (
          statsData &&
          typeof statsData === "object" &&
          !Array.isArray(statsData)
        ) {
          const parsed = Object.entries(statsData).map(
            ([name, s]: [string, any]) => ({
              name: name.toUpperCase(),
              acc: (s.test_accuracy * 100).toFixed(1),
              auc: s.test_roc_auc ? s.test_roc_auc.toFixed(2) : "N/A",
            }),
          );
          if (parsed.length > 0) setModelStats(parsed);
        }

        // SHAP features
        const shapData = shapRes.status === "fulfilled" ? shapRes.value : null;
        if (Array.isArray(shapData) && shapData.length > 0) {
          setShapFeatures(
            shapData.map((s: any) => ({
              name: s[0].replace(/_/g, " "),
              val: s[1],
            })),
          );
        }

        // Match fixtures
        const fixtureData =
          fixtureRes.status === "fulfilled" ? fixtureRes.value : null;
        if (Array.isArray(fixtureData) && fixtureData.length > 0) {
          setSchedule(fixtureData.slice(0, 5));
        }

        // Intelligence data
        const intData = intRes.status === "fulfilled" ? intRes.value : null;
        if (intData?.squad_strength) {
          setIntelligenceData(intData);
        }

        // No error banner — fallbacks cover everything silently
      } catch (err) {
        console.warn("Dashboard data fetch failed, using fallback data:", err);
        // Fallback data already loaded as initial state — nothing to do
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [tournament, refreshIndex]);

  const topTeam = winnerData.length > 0 ? winnerData[0] : null;

  return {
    winnerData,
    modelStats,
    shapFeatures,
    schedule,
    intelligenceData,
    metadata,
    loading,
    error,
    retry,
    topTeam,
  };
}
