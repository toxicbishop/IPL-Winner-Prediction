import React from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, BarChart, Bar } from "recharts";
import { api } from "../lib/api";
import { PageHeader } from "../components/kinetic/PageHeader";
import { Panel } from "../components/kinetic/Panel";
import { MetricTile } from "../components/kinetic/MetricTile";
import { getTeamLogo } from "../constants/teams";

export default function TeamDetail() {
  const { teamId } = useParams<{ teamId: string }>();
  const q = useQuery({ queryKey: ["team", teamId], queryFn: () => api.team(teamId!) });
  const t = q.data;
  if (!t) return null;

  return (
    <>
      <PageHeader
        eyebrow={<Link to="/teams" className="hover:text-[color:var(--color-primary)]">← All teams</Link>}
        title={
          <span className="flex items-center gap-3 text-[color:var(--color-text-main)]">
            <span className="inline-flex h-12 w-12 items-center justify-center rounded-md" style={{ background: t.color }}>
              {getTeamLogo(t.short) ? (
                <img
                  src={getTeamLogo(t.short)}
                  alt={`${t.name} logo`}
                  className="h-9 w-9 object-contain"
                />
              ) : (
                <span className="text-base not-italic font-display text-white font-bold">{t.short}</span>
              )}
            </span>
            {t.name}
          </span>
        }
        meta={`TITLES=${t.titles}  ·  PREDICTED_POS=${t.predictedFinish}`}
      />

      <section className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <MetricTile id="WP_NOW" label="Win Probability" value={t.winProb} suffix="%" />
        <MetricTile id="POS" label="Predicted Finish" value={`#${t.predictedFinish}`} accent="accent" />
        <MetricTile id="FORM_7" label="Form (last 7)" value={t.form.filter((x) => x === "W").length} suffix={`/${t.form.length}`} accent="destructive" />
      </section>

      <section className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Panel id="TRAJECTORY" status="ROUNDS 1–14" title="Win-prob trajectory">
          <div className="h-[260px]">
            <ResponsiveContainer>
              <LineChart data={t.trajectory}>
                <XAxis dataKey="round" tick={{ fontSize: 10, fontFamily: "var(--font-mono)" }} stroke="var(--color-text-muted)" />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fontFamily: "var(--font-mono)" }} stroke="var(--color-text-muted)" />
                <Tooltip
                  contentStyle={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", fontFamily: "var(--font-mono)", fontSize: 11 }}
                  labelStyle={{ color: "var(--color-text-main)", fontWeight: 600 }}
                  itemStyle={{ color: "var(--color-text-secondary)" }}
                />
                <Line type="monotone" dataKey="prob" stroke={t.color} strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel id="H2H" status="LAST 5 OPPONENTS" title="Head-to-head">
          <div className="h-[260px]">
            <ResponsiveContainer>
              <BarChart data={t.h2h}>
                <XAxis dataKey="opponent" tick={{ fontSize: 10, fontFamily: "var(--font-mono)" }} stroke="var(--color-text-muted)" />
                <YAxis tick={{ fontSize: 10, fontFamily: "var(--font-mono)" }} stroke="var(--color-text-muted)" />
                <Tooltip
                  contentStyle={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", fontFamily: "var(--font-mono)", fontSize: 11 }}
                  labelStyle={{ color: "var(--color-text-main)", fontWeight: 600 }}
                  itemStyle={{ color: "var(--color-text-secondary)" }}
                />
                <Bar dataKey="wins" fill="var(--color-secondary)" />
                <Bar dataKey="losses" fill="var(--color-tertiary)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </section>

      <section className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Panel id="SQUAD" status={`${t.squad.length} KEY PLAYERS`} title="Key squad">
          <ul className="divide-y divide-[color:var(--color-border)] font-mono-ui text-xs">
            {t.squad.map((p) => (
              <li key={p.name} className="flex justify-between py-2">
                <span>{p.name}</span>
                <span className="text-[color:var(--color-primary)]">{p.role}</span>
              </li>
            ))}
          </ul>
        </Panel>
        <Panel id="FORM" status="LAST 7" title="Form line">
          <div className="flex gap-2">
            {t.form.map((f, i) => (
              <span key={i} className={`inline-flex h-10 w-10 items-center justify-center font-display italic text-lg border ${f === "W" ? "border-[color:var(--color-secondary)] text-[color:var(--color-secondary)]" : "border-[color:var(--color-tertiary)] text-[color:var(--color-tertiary)]"}`}>{f}</span>
            ))}
          </div>
        </Panel>
      </section>
    </>
  );
}
