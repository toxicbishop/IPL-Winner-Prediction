import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import { PageHeader } from "../components/kinetic/PageHeader";
import { Panel } from "../components/kinetic/Panel";

export default function ArchivePage() {
  const q = useQuery({ queryKey: ["seasons"], queryFn: api.seasons });
  return (
    <>
      <PageHeader eyebrow="Historical Index" title="Archive" meta={`SEASONS=${q.data?.length ?? 0}`} />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {(q.data ?? []).map((s) => (
          <Link key={s.year} to={`/archive/${s.year}`}>
            <Panel id={`SEASON_${s.year}`} status={`ACC ${s.accuracy}%`} className="hover:border-[color:var(--color-primary)] transition">
              <p className="font-display italic text-5xl tabular-nums">{s.year}</p>
              <div className="etched my-3 h-1" />
              <div className="grid grid-cols-2 gap-3 font-mono-ui text-xs">
                <div>
                  <p className="uppercase tracking-widest text-[color:var(--color-text-muted)] text-[10px]">Champion</p>
                  <p className="text-[color:var(--color-primary)] text-base">{s.winner}</p>
                </div>
                <div>
                  <p className="uppercase tracking-widest text-[color:var(--color-text-muted)] text-[10px]">Runner-up</p>
                  <p className="text-base text-[color:var(--color-text-main)]">{s.runnerUp}</p>
                </div>
              </div>
            </Panel>
          </Link>
        ))}
      </div>
    </>
  );
}
