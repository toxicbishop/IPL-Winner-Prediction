import * as React from "react";

interface Props {
  eyebrow?: React.ReactNode;
  title: React.ReactNode;
  meta?: React.ReactNode;
  right?: React.ReactNode;
}

export function PageHeader({ eyebrow, title, meta, right }: Props) {
  return (
    <header className="mb-6 flex flex-col gap-4 border-b border-border pb-6 md:flex-row md:items-end md:justify-between">
      <div>
        {eyebrow ? (
          <p className="font-mono-ui text-[10px] uppercase tracking-widest text-muted-foreground">
            — {eyebrow}
          </p>
        ) : null}
        <h1 className="font-display text-5xl italic leading-none tracking-tight md:text-6xl">
          {title}
          <span className="ml-2 text-primary">✦</span>
        </h1>
        {meta ? (
          <div className="mt-2 font-mono-ui text-[10px] uppercase tracking-widest text-muted-foreground">
            {meta}
          </div>
        ) : null}
      </div>
      {right ? <div className="flex items-center gap-2">{right}</div> : null}
    </header>
  );
}
