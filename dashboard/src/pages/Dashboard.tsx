import React from "react";
import { Link } from "react-router-dom";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, RadarChart, PolarGrid, PolarAngleAxis, Radar } from "recharts";
import { ArrowUpRight, BrainCircuit, Database, Layers, TrendingUp } from "lucide-react";
import { PageHeader } from "../components/kinetic/PageHeader";
import { MetricTile } from "../components/kinetic/MetricTile";
import { Panel } from "../components/kinetic/Panel";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

import HeroChampion from "../components/HeroChampion";
import StatCards from "../components/StatCards";
import WinProbabilityChart from "../components/WinProbabilityChart";
import FeatureRadar from "../components/FeatureRadar";
import MatchForecast from "../components/MatchForecast";
import TeamInsights from "../components/TeamInsights";
import { ErrorBanner } from "../components/ApiState";

export default function DashboardPage({ dashboardData }: { dashboardData: any }) {
  const summary = useQuery({ queryKey: ["summary"], queryFn: api.summary });
  const wp = useQuery({ queryKey: ["wp"], queryFn: api.winProbability });
  const fi = useQuery({ queryKey: ["fi"], queryFn: api.featureImportance });
  const ql = useQuery({ queryKey: ["ql"], queryFn: api.qualitative });
  const up = useQuery({ queryKey: ["up"], queryFn: api.upcoming });

  const s = summary.data;
  const wpData = wp.data?.series ?? [];

  const {
    winnerData,
    modelStats,
    shapFeatures,
    schedule,
    loading,
    error,
    retry,
    topTeam,
  } = dashboardData;

  return (
    <>
      <PageHeader
        eyebrow="Kinetic Monolith v1.1 · AI Platform"
        title="IPL 2026"
      />

      {error && <ErrorBanner message={error} onRetry={retry} />}

      <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricTile id="ACC_087" label="Ensemble Accuracy" value={s?.ensembleAccuracy ?? "—"} suffix="%" accent="primary" icon={<BrainCircuit className="h-3.5 w-3.5" />} />
        <MetricTile id="MDL_014" label="Models Polled" value={s?.modelsPolled ?? "—"} accent="accent" icon={<Layers className="h-3.5 w-3.5" />} />
        <MetricTile id="DAT_1169" label="Matches Analyzed" value={(s?.matchesAnalyzed ?? 0).toLocaleString()} accent="primary" icon={<Database className="h-3.5 w-3.5" />} />
        <MetricTile id="FEAT_01" label="Top Feature" value={<span className="text-2xl">{s?.topFeature ?? "—"}</span>} accent="destructive" icon={<ArrowUpRight className="h-3.5 w-3.5" />} />
      </section>

      {/* Existing App content integrated */}
      <div className="mt-6 mb-6">
         <HeroChampion topTeam={topTeam} loading={loading} />
         <StatCards
            modelStats={modelStats}
            shapFeatures={shapFeatures}
            loading={loading}
         />
         <div className="two-col-grid mt-6">
            <WinProbabilityChart data={winnerData} loading={loading} />
            <FeatureRadar data={shapFeatures} loading={loading} />
         </div>
         <TeamInsights teams={winnerData} loading={loading} />
         <MatchForecast schedule={schedule} loading={loading} />
      </div>

      <section className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Panel id="CHART_ID: WIN_PROB_01" status="LIVE" title="Win Probability (Match-level Simulation)">
          <div className="flex items-center justify-between font-mono-ui text-[10px] uppercase tracking-widest text-[color:var(--color-text-muted)]">
            <span>{wp.data?.home}</span>
            <span>vs</span>
            <span>{wp.data?.away}</span>
          </div>
          <div className="mt-3 h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={wpData}>
                <defs>
                  <linearGradient id="wpHome" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="wpAway" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--color-secondary)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="var(--color-secondary)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="over" stroke="var(--color-text-muted)" tick={{ fontSize: 10, fontFamily: "var(--font-mono)" }} />
                <YAxis stroke="var(--color-text-muted)" tick={{ fontSize: 10, fontFamily: "var(--font-mono)" }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", fontFamily: "var(--font-mono)", fontSize: 11 }}
                  labelStyle={{ color: "var(--color-text-main)", fontWeight: 600 }}
                  itemStyle={{ color: "var(--color-text-secondary)" }}
                />
                <Area type="monotone" dataKey="home" stroke="var(--color-primary)" strokeWidth={2} fill="url(#wpHome)" />
                <Area type="monotone" dataKey="away" stroke="var(--color-secondary)" strokeWidth={2} fill="url(#wpAway)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel id="PROC_ID: SHAP_RADAR" status="FEAT_01-06" title="Feature Importance">
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={fi.data ?? []}>
                <PolarGrid stroke="var(--color-border)" />
                <PolarAngleAxis dataKey="feature" tick={{ fontSize: 10, fontFamily: "var(--font-mono)", fill: "var(--color-text-main)" }} />
                <Radar dataKey="value" stroke="var(--color-primary)" fill="var(--color-primary)" fillOpacity={0.35} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </section>

      <section className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-5">
        <Panel id="INSIGHT_ID: TEAM_QUALITATIVE_BREAKDOWN" status="LIVE_SIGNALS" title="Why they are winning (or losing)" className="lg:col-span-3">
          <div className="grid gap-4 sm:grid-cols-2">
            {(ql.data ?? []).map((q) => (
              <div key={q.team} className="border border-dashed border-[color:var(--color-border)] p-3">
                <div className="flex items-center justify-between">
                  <p className="font-display italic text-lg">{q.team}</p>
                  <span className="font-mono-ui text-[10px] uppercase tracking-widest text-[color:var(--color-primary)]">
                    {q.sentiment}
                  </span>
                </div>
                <ul className="mt-2 space-y-1 font-mono-ui text-xs text-[color:var(--color-text-muted)]">
                  {q.reasons.map((r) => (
                    <li key={r} className="flex gap-2"><TrendingUp className="h-3 w-3 mt-0.5 text-[color:var(--color-secondary)]" />{r}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Panel>

        <Panel id="SCHED_ID: FIXT_UPCOMING" status={`${up.data?.length ?? 0} SLOTS`} title="Match Forecast" className="lg:col-span-2">
          <table className="w-full font-mono-ui text-xs">
            <thead className="text-[color:var(--color-text-muted)]">
              <tr className="border-b border-dashed border-[color:var(--color-border)]">
                <th className="py-2 text-left">Date</th>
                <th className="text-left">Match</th>
                <th className="text-right">Pred</th>
                <th className="text-right">Conf</th>
              </tr>
            </thead>
            <tbody>
              {(up.data ?? []).map((m) => (
                <tr key={m.date} className="border-b border-[color:var(--color-border)] opacity-80">
                  <td className="py-2 text-[color:var(--color-text-muted)]">{m.date.slice(5)}</td>
                  <td>{m.home} v {m.away}</td>
                  <td className="text-right text-[color:var(--color-primary)]">{m.predicted}</td>
                  <td className="text-right">{Math.round(m.confidence * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      </section>

      <section className="mt-3">
        <Panel id="NAV_ID: EXPLORE_MORE" status="QUICK LINKS" title="Dive deeper">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 font-mono-ui text-[11px] uppercase tracking-widest">
            <Link to="/teams" className="border border-[color:var(--color-border)] p-4 hover:bg-[color:var(--color-surface-high)] transition">→ Browse teams</Link>
            <Link to="/players" className="border border-[color:var(--color-border)] p-4 hover:bg-[color:var(--color-surface-high)] transition">→ Player profiles</Link>
            <Link to="/archive" className="border border-[color:var(--color-border)] p-4 hover:bg-[color:var(--color-surface-high)] transition">→ Past seasons</Link>
            <Link to="/about" className="border border-[color:var(--color-border)] p-4 hover:bg-[color:var(--color-surface-high)] transition">→ Methodology</Link>
          </div>
        </Panel>
      </section>
    </>
  );
}
