import React from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";
import { api } from "../lib/api";
import { PageHeader } from "../components/kinetic/PageHeader";
import { Panel } from "../components/kinetic/Panel";
import { MetricTile } from "../components/kinetic/MetricTile";

export default function PlayerDetail() {
  const { playerId } = useParams<{ playerId: string }>();
  const q = useQuery({ queryKey: ["player", playerId], queryFn: () => api.player(playerId!) });
  const p = q.data;
  if (!p) return null;

  return (
    <>
      <PageHeader
        eyebrow={<Link to="/players" className="hover:text-[color:var(--color-primary)]">← Players</Link>}
        title={p.name}
        meta={`${p.team}  ·  ${p.role}  ·  ${p.nationality}`}
      />

      <section className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <MetricTile id="MAT" label="Matches" value={p.career.matches} accent="foreground" />
        <MetricTile id="RUNS" label="Runs" value={p.career.runs.toLocaleString()} />
        <MetricTile id="WKT" label="Wickets" value={p.career.wickets} accent="accent" />
        <MetricTile id="SR" label="Strike Rate" value={p.career.strikeRate.toFixed(1)} accent="destructive" />
      </section>

      <section className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Panel id="FORM_10" status="LAST 10" title="Recent form">
          <div className="h-[260px]">
            <ResponsiveContainer>
              <BarChart data={p.last10}>
                <XAxis dataKey="match" tick={{ fontSize: 10, fontFamily: "var(--font-mono)" }} stroke="var(--color-text-muted)" />
                <YAxis tick={{ fontSize: 10, fontFamily: "var(--font-mono)" }} stroke="var(--color-text-muted)" />
                <Tooltip
                  contentStyle={{ background: "var(--color-surface)", border: "1px solid var(--color-border)", fontFamily: "var(--font-mono)", fontSize: 11 }}
                  labelStyle={{ color: "var(--color-text-main)", fontWeight: 600 }}
                  itemStyle={{ color: "var(--color-text-secondary)" }}
                />
                <Bar dataKey="score" fill="var(--color-primary)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel id="IMPACT" status="ROLE-WEIGHTED" title="Impact breakdown">
          <ul className="space-y-3 font-mono-ui text-xs">
            {[
              { k: "Form Rating", v: p.form },
              { k: "Impact Score", v: p.impact },
              { k: "Avg", v: p.career.average },
              { k: "Strike Rate", v: p.career.strikeRate },
            ].map((row) => (
              <li key={row.k}>
                <div className="flex justify-between">
                  <span className="uppercase tracking-widest text-[color:var(--color-text-muted)] text-[10px]">{row.k}</span>
                  <span className="text-[color:var(--color-primary)]">{row.v}</span>
                </div>
                <div className="mt-1 h-1.5 w-full bg-[color:var(--color-surface-high)]">
                  <div className="h-full bg-[color:var(--color-primary)]" style={{ width: `${Math.min(100, Number(row.v))}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </Panel>
      </section>
    </>
  );
}
