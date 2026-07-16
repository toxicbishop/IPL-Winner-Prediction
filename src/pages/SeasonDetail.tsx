import React from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import { PageHeader } from "../components/kinetic/PageHeader";
import { Panel } from "../components/kinetic/Panel";
import { MetricTile } from "../components/kinetic/MetricTile";

export default function SeasonDetail() {
  const { season } = useParams<{ season: string }>();
  const q = useQuery({ queryKey: ["season", season], queryFn: () => api.season(season!) });
  const s = q.data;
  if (!s) return null;

  return (
    <>
      <PageHeader
        eyebrow={<Link to="/archive" className="hover:text-[color:var(--color-primary)]">← Archive</Link>}
        title={`Season ${s.year}`}
        meta={`CHAMPION=${s.winner}  ·  ACC=${s.accuracy}%`}
      />

      <section className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <MetricTile id="CHAMP" label="Champion" value={<span className="text-3xl text-[color:var(--color-text-main)]">{s.winner}</span>} />
        <MetricTile id="RUNNER" label="Runner-up" value={<span className="text-3xl text-[color:var(--color-text-main)]">{s.runnerUp}</span>} accent="accent" />
        <MetricTile id="ACC" label="Model Accuracy" value={s.accuracy} suffix="%" accent="destructive" />
      </section>

      <section className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Panel id="FINAL" status="GRAND FINAL" title="Final scoreboard">
          <div className="space-y-3 font-mono-ui text-sm text-[color:var(--color-text-main)]">
            <div className="flex justify-between border-b border-dashed border-[color:var(--color-border)] pb-2">
              <span>{s.finalScore.home}</span>
              <span className="text-[color:var(--color-primary)]">WON</span>
            </div>
            <div className="flex justify-between">
              <span>{s.finalScore.away}</span>
              <span className="text-[color:var(--color-text-muted)]">—</span>
            </div>
          </div>
        </Panel>

        <Panel id="TOP_FEAT" status="MODEL DRIVERS" title="Top features">
          <ul className="space-y-2 font-mono-ui text-xs">
            {s.topFeatures.map((f, i) => (
              <li key={f} className="flex items-center gap-3">
                <span className="text-[color:var(--color-text-muted)]">0{i + 1}</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </Panel>
      </section>

      <section className="mt-3">
        <Panel id="PVA" status="PREDICTED vs ACTUAL" title="Playoff predictions">
          <table className="w-full font-mono-ui text-xs text-[color:var(--color-text-main)]">
            <thead className="text-[color:var(--color-text-muted)]">
              <tr className="border-b border-dashed border-[color:var(--color-border)]">
                <th className="py-2 text-left">Match</th>
                <th className="text-left">Predicted</th>
                <th className="text-left">Actual</th>
                <th className="text-right">Hit</th>
              </tr>
            </thead>
            <tbody>
              {s.predictions.map((p) => (
                <tr key={p.match} className="border-b border-[color:var(--color-border)] opacity-80">
                  <td className="py-2">{p.match}</td>
                  <td className="text-[color:var(--color-primary)]">{p.predicted}</td>
                  <td>{p.actual}</td>
                  <td className="text-right">{p.predicted === p.actual ? "✓" : "✗"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      </section>
    </>
  );
}
