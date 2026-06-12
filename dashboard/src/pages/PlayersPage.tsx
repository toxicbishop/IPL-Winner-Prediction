import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { api } from "../lib/api";
import { PageHeader } from "../components/kinetic/PageHeader";
import { Panel } from "../components/kinetic/Panel";

const ROLES = ["ALL", "BAT", "BOWL", "ALL_R", "WK"] as const;

export default function PlayersPage() {
  const q = useQuery({ queryKey: ["players"], queryFn: api.players });
  const [search, setSearch] = useState("");
  const [role, setRole] = useState<string>("ALL");

  const filtered = useMemo(() => {
    return (q.data ?? []).filter((p) => {
      if (role !== "ALL" && p.role !== role) return false;
      if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [q.data, search, role]);

  return (
    <>
      <PageHeader eyebrow="Player Index · Impact-ranked" title="Players" meta={`SHOWING=${filtered.length}`} />

      <div className="mb-4 flex flex-col gap-2 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[color:var(--color-text-muted)]" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="SEARCH PLAYER" className="w-full rounded-md border border-[color:var(--color-border)] bg-[color:var(--color-surface)] pl-9 pr-3 py-2 font-mono-ui text-xs uppercase tracking-widest placeholder:text-[color:var(--color-text-muted)] focus:outline-none focus:border-[color:var(--color-primary)] text-[color:var(--color-text-main)]" />
        </div>
        <div className="flex gap-1">
          {ROLES.map((r) => (
            <button key={r} onClick={() => setRole(r)} className={"rounded-md border px-3 py-2 font-mono-ui text-[10px] uppercase tracking-widest " + (role === r ? "border-[color:var(--color-primary)] text-[color:var(--color-primary)] bg-[color:var(--color-surface-high)]" : "border-[color:var(--color-border)] text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-main)]")}>{r}</button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((p) => (
          <Link key={p.id} to={`/players/${p.id}`}>
            <Panel id={`PLR_${p.id.toUpperCase()}`} status={p.team} className="hover:border-[color:var(--color-primary)] transition">
              <div className="flex items-baseline justify-between text-[color:var(--color-text-main)]">
                <p className="font-display italic text-xl">{p.name}</p>
                <span className="font-mono-ui text-[10px] uppercase tracking-widest text-[color:var(--color-text-muted)]">{p.nationality}</span>
              </div>
              <div className="etched my-3 h-1" />
              <div className="grid grid-cols-2 gap-2 font-mono-ui text-xs">
                <div>
                  <p className="text-[color:var(--color-text-muted)] uppercase tracking-widest text-[10px]">Form</p>
                  <p className="font-display italic text-2xl text-[color:var(--color-primary)]">{p.form}</p>
                </div>
                <div>
                  <p className="text-[color:var(--color-text-muted)] uppercase tracking-widest text-[10px]">Impact</p>
                  <p className="font-display italic text-2xl text-[color:var(--color-secondary)]">{p.impact}</p>
                </div>
              </div>
            </Panel>
          </Link>
        ))}
      </div>
    </>
  );
}
