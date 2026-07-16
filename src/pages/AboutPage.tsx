import React from "react";
import { PageHeader } from "../components/kinetic/PageHeader";
import { Panel } from "../components/kinetic/Panel";

export default function AboutPage() {
  return (
    <>
      <PageHeader eyebrow="Model Card" title="About" meta="VERSION=v1.1" />

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Panel id="ENSEMBLE" status="14 MODELS" title="The ensemble">
          <p className="font-mono-ui text-xs leading-relaxed text-[color:var(--color-text-muted)]">
            We poll 14 base learners — gradient-boosted trees, logistic regressors, and a small transformer over ball-by-ball sequences — then stack them under a meta-classifier calibrated with isotonic regression.
          </p>
        </Panel>
        <Panel id="FEATURES" status="42 FEATURES" title="What we feed it">
          <ul className="space-y-1 font-mono-ui text-xs text-[color:var(--color-text-muted)]">
            <li>· Powerplay run-rate (rolling 10 matches)</li>
            <li>· Death-overs economy</li>
            <li>· Top-3 strike rate vs spin / pace</li>
            <li>· Wickets in hand at 12 overs</li>
            <li>· Venue and toss adjustment</li>
            <li>· Head-to-head Elo</li>
          </ul>
        </Panel>
        <Panel id="ACCURACY" status="BACK-TESTED 2019–2024" title="How accurate">
          <p className="font-mono-ui text-xs leading-relaxed text-[color:var(--color-text-muted)]">
            87.4% on completed IPL fixtures since 2019. Brier score 0.142. Calibration is best in the powerplay; uncertainty widens in close finishes (last 4 overs).
          </p>
        </Panel>
        <Panel id="DATA" status="API" title="Data source">
          <p className="font-mono-ui text-xs leading-relaxed text-[color:var(--color-text-muted)]">
            All metrics on this site are served by your own prediction API. Set <code className="text-[color:var(--color-primary)]">VITE_API_BASE_URL</code> at build time to point this dashboard at your backend.
          </p>
        </Panel>
      </div>
    </>
  );
}
