export const teamRows = [
  { id: "rcb", name: "Royal Challengers Bengaluru", short: "RCB", color: "#d71920", titles: 1, predictedFinish: 1, winProb: 22.5, trend: 3.05, confidence: "High" },
  { id: "gt", name: "Gujarat Titans", short: "GT", color: "#1b2a4a", titles: 1, predictedFinish: 2, winProb: 20.1, trend: 2.1, confidence: "High" },
  { id: "srh", name: "Sunrisers Hyderabad", short: "SRH", color: "#f26522", titles: 1, predictedFinish: 3, winProb: 18.7, trend: 0.91, confidence: "High" },
  { id: "rr", name: "Rajasthan Royals", short: "RR", color: "#ea1a85", titles: 1, predictedFinish: 4, winProb: 14.2, trend: 0.5, confidence: "Medium" },
  { id: "pbks", name: "Punjab Kings", short: "PBKS", color: "#a51d2d", titles: 0, predictedFinish: 5, winProb: 7.8, trend: 0.3, confidence: "Low" },
  { id: "kkr", name: "Kolkata Knight Riders", short: "KKR", color: "#3a225d", titles: 3, predictedFinish: 6, winProb: 7.2, trend: -0.4, confidence: "Low" },
  { id: "dc", name: "Delhi Capitals", short: "DC", color: "#17449b", titles: 0, predictedFinish: 7, winProb: 5.1, trend: -1.1, confidence: "Low" },
  { id: "mi", name: "Mumbai Indians", short: "MI", color: "#045093", titles: 5, predictedFinish: 8, winProb: 0, trend: -0.27, confidence: "Eliminated" },
  { id: "lsg", name: "Lucknow Super Giants", short: "LSG", color: "#0f4d92", titles: 0, predictedFinish: 9, winProb: 0, trend: -1.5, confidence: "Eliminated" },
  { id: "csk", name: "Chennai Super Kings", short: "CSK", color: "#f9cd05", titles: 5, predictedFinish: 10, winProb: 0, trend: -0.51, confidence: "Eliminated" },
];

export const summary = {
  ensembleAccuracy: 58.2,
  modelsPolled: 5,
  matchesAnalyzed: 1169,
  topFeature: "Powerplay Run Rate",
};

export const winnerProbabilities = {
  model_type: "Stacked temporal ensemble",
  validation_accuracy_2024: 58.2,
  data_coverage: "Cricsheet IPL ball-by-ball + engineered temporal features",
  last_updated: "2026-06-10T18:30:00Z",
  rankings: teamRows.map((team) => ({
    team_id: team.short,
    win_probability: team.winProb,
    trend: team.trend,
    confidence: team.confidence,
    explanation: {
      why:
        team.short === "RCB"
          ? ["table-topping form", "batting firepower", "strong net run rate"]
          : team.short === "GT"
            ? ["squad depth", "spin bowling coverage", "stable top order"]
            : ["positive recent form", "playoff path remains open"],
      risk:
        team.winProb === 0
          ? ["eliminated from contention"]
          : ["sport variance", "toss and venue sensitivity"],
    },
  })),
};

export const modelPerformance = {
  ensemble: { test_accuracy: 0.582, test_roc_auc: 0.62, test_f1: 0.59 },
  lightgbm: { test_accuracy: 0.569, test_roc_auc: 0.6, test_f1: 0.57 },
  xgboost: { test_accuracy: 0.551, test_roc_auc: 0.59, test_f1: 0.55 },
  random_forest: { test_accuracy: 0.542, test_roc_auc: 0.57, test_f1: 0.54 },
  extra_trees: { test_accuracy: 0.536, test_roc_auc: 0.56, test_f1: 0.53 },
};

export const shapImportance: [string, number][] = [
  ["powerplay_run_rate", 0.142],
  ["death_overs_economy", 0.118],
  ["top_3_strike_rate", 0.098],
  ["wickets_in_hand", 0.087],
  ["venue_advantage", 0.076],
  ["head_to_head_elo", 0.065],
];

export const intelligence = {
  squad_strength: { RCB: 8.9, GT: 8.7, SRH: 8.5, RR: 7.8, PBKS: 7.2, KKR: 7.0, DC: 6.8, CSK: 6.2, MI: 5.8, LSG: 5.5 },
  playoff_rate: { RCB: 0.59, GT: 0.67, SRH: 0.53, RR: 0.41, PBKS: 0.24, KKR: 0.65, DC: 0.47, CSK: 0, MI: 0, LSG: 0 },
  form_score: { RCB: 8.8, GT: 8.5, SRH: 8.3, RR: 7.4, PBKS: 6.8, KKR: 6.5, DC: 6.1, CSK: 5.2, MI: 4.8, LSG: 4.5 },
};

export const matchFixtures = [
  { date: "2027-05-26", team1: "RCB", team2: "GT", predicted_winner: "RCB", win_probability: 0.54 },
  { date: "2027-05-27", team1: "SRH", team2: "RR", predicted_winner: "SRH", win_probability: 0.61 },
  { date: "2027-05-29", team1: "GT", team2: "SRH", predicted_winner: "GT", win_probability: 0.55 },
  { date: "2027-05-31", team1: "RCB", team2: "GT", predicted_winner: "RCB", win_probability: 0.52 },
];

export const winProb = {
  matchId: "IPL-2027-FINAL-SIM",
  home: "RCB",
  away: "GT",
  series: Array.from({ length: 20 }, (_, i) => ({
    over: i + 1,
    home: Math.round(50 + Math.sin(i / 3) * 8 + i * 0.7),
    away: Math.round(50 - Math.sin(i / 3) * 8 - i * 0.7),
  })),
};

export const featureImportance = shapImportance.map(([feature, value]) => ({
  feature: feature.replace(/_/g, " "),
  value: Math.round(value * 1000),
}));

export const qualitative = [
  { team: "RCB", sentiment: "positive" as const, reasons: ["Table-topping form", "High top-order impact", "Strong NRR signal"] },
  { team: "GT", sentiment: "positive" as const, reasons: ["Stable bowling mix", "Spin-friendly matchups", "Consistent playoff baseline"] },
  { team: "SRH", sentiment: "watch" as const, reasons: ["Explosive batting", "High variance profile", "Strong chase upside"] },
];

export const upcoming = matchFixtures.map((match) => ({
  date: match.date,
  home: match.team1,
  away: match.team2,
  predicted: match.predicted_winner,
  confidence: match.win_probability ?? 0.5,
}));

export const teams = teamRows;

export const teamDetail = (id: string) => {
  const t = teams.find((x) => x.id === id || x.short.toLowerCase() === id.toLowerCase()) ?? teams[0];
  return {
    ...t,
    form: ["W", "W", "L", "W", "L", "W", "W"] as const,
    squad: [
      { name: "Top-order anchor", role: "BAT" },
      { name: "Powerplay hitter", role: "BAT" },
      { name: "Middle-over all-rounder", role: "ALL" },
      { name: "Death bowler", role: "BOWL" },
      { name: "Wicketkeeper finisher", role: "WK" },
    ],
    h2h: teams.filter((x) => x.id !== t.id).slice(0, 5).map((x, index) => ({
      opponent: x.short,
      wins: 5 + index,
      losses: 4 + (index % 3),
    })),
    trajectory: Array.from({ length: 14 }, (_, i) => ({
      round: i + 1,
      prob: Math.max(0, Math.min(30, t.winProb + Math.sin(i / 2) * 2 + i * 0.1)),
    })),
  };
};

export const players = [
  { id: "p1", name: "Virat Kohli", team: "RCB", role: "BAT", form: 88, impact: 93, nationality: "IND" },
  { id: "p2", name: "Shubman Gill", team: "GT", role: "BAT", form: 86, impact: 89, nationality: "IND" },
  { id: "p3", name: "Travis Head", team: "SRH", role: "BAT", form: 86, impact: 84, nationality: "AUS" },
  { id: "p4", name: "Rashid Khan", team: "GT", role: "BOWL", form: 87, impact: 90, nationality: "AFG" },
  { id: "p5", name: "Jasprit Bumrah", team: "MI", role: "BOWL", form: 90, impact: 95, nationality: "IND" },
  { id: "p6", name: "Sanju Samson", team: "RR", role: "WK", form: 78, impact: 80, nationality: "IND" },
];

export const playerDetail = (id: string) => {
  const p = players.find((x) => x.id === id) ?? players[0];
  return {
    ...p,
    career: {
      matches: 160 + Number(p.id.slice(1)) * 7,
      runs: p.role === "BOWL" ? 420 : 4200 + Number(p.id.slice(1)) * 120,
      wickets: p.role === "BOWL" ? 145 + Number(p.id.slice(1)) * 4 : 8,
      average: 36.4,
      strikeRate: 141.7,
    },
    last10: Array.from({ length: 10 }, (_, i) => ({ match: i + 1, score: 28 + ((i * 13 + Number(p.id.slice(1))) % 62) })),
  };
};

export const seasons = [
  { year: "2026", winner: "RCB", runnerUp: "GT", accuracy: 58.2 },
  { year: "2025", winner: "RCB", runnerUp: "PBKS", accuracy: 60.1 },
  { year: "2024", winner: "KKR", runnerUp: "SRH", accuracy: 58.8 },
  { year: "2023", winner: "CSK", runnerUp: "GT", accuracy: 57.9 },
  { year: "2022", winner: "GT", runnerUp: "RR", accuracy: 56.7 },
  { year: "2021", winner: "CSK", runnerUp: "KKR", accuracy: 56.2 },
  { year: "2020", winner: "MI", runnerUp: "DC", accuracy: 55.6 },
];

export const seasonDetail = (year: string) => {
  const s = seasons.find((x) => x.year === year) ?? seasons[0];
  return {
    ...s,
    finalScore: { home: `${s.winner} 168/4`, away: `${s.runnerUp} 162/8` },
    topFeatures: ["Powerplay RR", "Death Econ", "Spin %", "Toss"],
    predictions: Array.from({ length: 8 }, (_, i) => ({
      match: `Validation match ${i + 1}`,
      predicted: i % 2 ? s.winner : s.runnerUp,
      actual: i % 3 ? s.winner : s.runnerUp,
    })),
  };
};

export function simulateH2H(team1: string, team2: string) {
  const a = teams.find((team) => team.id === team1 || team.short === team1.toUpperCase()) ?? teams[0];
  const b = teams.find((team) => team.id === team2 || team.short === team2.toUpperCase()) ?? teams[1];
  const total = Math.max(1, a.winProb + b.winProb);
  return {
    team1: a.short,
    team2: b.short,
    simulations: 5000,
    team1_win_probability: Number((a.winProb / total).toFixed(3)),
    team2_win_probability: Number((b.winProb / total).toFixed(3)),
    predicted_winner: a.winProb >= b.winProb ? a.short : b.short,
  };
}
