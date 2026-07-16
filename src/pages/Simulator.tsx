import React, { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Swords } from "lucide-react";
import { api } from "../lib/api";
import { PageHeader } from "../components/kinetic/PageHeader";
import { Panel } from "../components/kinetic/Panel";

export default function Simulator() {
  const teamsQ = useQuery({ queryKey: ["teams"], queryFn: api.teams });
  const teams = teamsQ.data ?? [];
  const [home, setHome] = useState("mi");
  const [away, setAway] = useState("csk");
  const [venue, setVenue] = useState("Wankhede");

  const result = useMemo(() => {
    const h = teams.find((t) => t.id === home);
    const a = teams.find((t) => t.id === away);
    if (!h || !a) return { home: 50, away: 50 };
    const venueBoost = venue === "Wankhede" ? 6 : venue === "Chepauk" ? 4 : 2;
    const hScore = h.winProb + venueBoost;
    const aScore = a.winProb;
    const total = hScore + aScore;
    return { home: Math.round((hScore / total) * 100), away: Math.round((aScore / total) * 100) };
  }, [teams, home, away, venue]);

  return (
    <>
      <PageHeader eyebrow="What-if Engine" title="Simulator" meta="MODE=DUEL" />

      <Panel id="DUEL_INPUT" status="CONFIGURE" title="Set up the duel">
        <div className="grid gap-3 sm:grid-cols-3">
          <Field label="Home" value={home} onChange={setHome} options={teams.map((t) => ({ value: t.id, label: t.name }))} />
          <Field label="Away" value={away} onChange={setAway} options={teams.map((t) => ({ value: t.id, label: t.name }))} />
          <Field label="Venue" value={venue} onChange={setVenue} options={["Wankhede", "Chepauk", "Eden Gardens", "Chinnaswamy", "Narendra Modi"].map((v) => ({ value: v, label: v }))} />
        </div>
      </Panel>

      <Panel id="DUEL_OUTPUT" status="LIVE" title="Predicted win probability" className="mt-3">
        <div className="flex items-center justify-center gap-6 py-6">
          <div className="text-center">
            <p className="font-mono-ui text-[10px] uppercase tracking-widest text-[color:var(--color-text-muted)]">{teams.find((t) => t.id === home)?.short}</p>
            <p className="font-display italic text-7xl text-[color:var(--color-primary)] tabular-nums">{result.home}%</p>
          </div>
          <Swords className="h-8 w-8 text-[color:var(--color-text-muted)]" />
          <div className="text-center">
            <p className="font-mono-ui text-[10px] uppercase tracking-widest text-[color:var(--color-text-muted)]">{teams.find((t) => t.id === away)?.short}</p>
            <p className="font-display italic text-7xl text-[color:var(--color-secondary)] tabular-nums">{result.away}%</p>
          </div>
        </div>
        <div className="flex h-3 w-full overflow-hidden border border-[color:var(--color-border)]">
          <div className="bg-[color:var(--color-primary)]" style={{ width: `${result.home}%` }} />
          <div className="bg-[color:var(--color-secondary)]" style={{ width: `${result.away}%` }} />
        </div>
      </Panel>
    </>
  );
}

function Field({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: { value: string; label: string }[] }) {
  return (
    <label className="block">
      <span className="font-mono-ui text-[10px] uppercase tracking-widest text-[color:var(--color-text-muted)]">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)} className="mt-1 w-full rounded-md border border-[color:var(--color-border)] bg-[color:var(--color-surface)] px-3 py-2 font-mono-ui text-xs uppercase tracking-widest focus:outline-none focus:border-[color:var(--color-primary)] text-[color:var(--color-text-main)]">
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </label>
  );
}
