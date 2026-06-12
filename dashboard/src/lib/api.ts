// Typed API client. Set VITE_API_BASE_URL to point at your backend.
// When unset, falls back to local mock data so the UI is fully functional.
import * as mock from "./mock-data";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

async function get<T>(path: string, fallback: T): Promise<T> {
  if (!BASE) return fallback;
  try {
    const res = await fetch(`${BASE}${path}`);
    if (!res.ok) throw new Error(String(res.status));
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

export const api = {
  summary: () => get("/metrics/summary", mock.summary),
  winProbability: () => get("/predictions/win-probability", mock.winProb),
  featureImportance: () => get("/features/importance", mock.featureImportance),
  qualitative: () => get("/insights/qualitative", mock.qualitative),
  upcoming: () => get("/matches/upcoming", mock.upcoming),
  teams: () => get("/teams", mock.teams),
  team: (id: string) => get(`/teams/${id}`, mock.teamDetail(id)),
  players: () => get("/players", mock.players),
  player: (id: string) => get(`/players/${id}`, mock.playerDetail(id)),
  seasons: () => get("/seasons", mock.seasons),
  season: (year: string) => get(`/seasons/${year}`, mock.seasonDetail(year)),
};

export type Summary = typeof mock.summary;
export type Team = (typeof mock.teams)[number];
export type Player = (typeof mock.players)[number];
export type Season = (typeof mock.seasons)[number];