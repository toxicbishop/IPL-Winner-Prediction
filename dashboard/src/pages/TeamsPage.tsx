import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import { PageHeader } from "../components/kinetic/PageHeader";
import { Panel } from "../components/kinetic/Panel";
import { getTeamLogo } from "../constants/teams";

export default function TeamsPage() {
  const teams = useQuery({ queryKey: ["teams"], queryFn: api.teams });
  const sorted = [...(teams.data ?? [])].sort((a, b) => a.predictedFinish - b.predictedFinish);

  return (
    <>
      <PageHeader eyebrow="Franchises · 10 Teams" title="Teams" meta={`COUNT=${sorted.length}`} />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {sorted.map((t) => (
          <Link key={t.id} to={`/teams/${t.id}`}>
            <Panel id={`TEAM_${t.short}`} status={`POS ${t.predictedFinish}`} className="hover:border-[color:var(--color-primary)] transition">
              <div className="flex items-center gap-3">
                <span className="flex h-12 w-12 items-center justify-center rounded-md" style={{ background: t.color }}>
                  {getTeamLogo(t.short) ? (
                    <img
                      src={getTeamLogo(t.short)}
                      alt={`${t.name} logo`}
                      className="h-9 w-9 object-contain animate-fade-in"
                    />
                  ) : (
                    <span className="font-display italic text-lg text-white font-bold">{t.short}</span>
                  )}
                </span>
                <div>
                  <p className="font-display italic text-lg leading-tight">{t.name}</p>
                  <p className="font-mono-ui text-[10px] uppercase tracking-widest text-[color:var(--color-text-muted)]">{t.titles} TITLES</p>
                </div>
              </div>
              <div className="etched mt-3 h-1" />
              <div className="mt-3 flex items-end justify-between">
                <span className="font-mono-ui text-[10px] uppercase tracking-widest text-[color:var(--color-text-muted)]">Win Prob</span>
                <span className="font-display italic text-3xl text-[color:var(--color-primary)] tabular-nums">{t.winProb}%</span>
              </div>
              <div className="mt-2 h-1.5 w-full bg-[color:var(--color-surface-high)]">
                <div className="h-full bg-[color:var(--color-primary)]" style={{ width: `${t.winProb}%` }} />
              </div>
            </Panel>
          </Link>
        ))}
      </div>
    </>
  );
}
