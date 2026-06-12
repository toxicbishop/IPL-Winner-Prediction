import * as React from "react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface PanelProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title" | "id"> {
  id?: string;
  status?: string;
  title?: React.ReactNode;
  children: React.ReactNode;
}

export function Panel({ id, status, title, children, className, ...rest }: PanelProps) {
  return (
    <div className={cn("panel", className)} {...rest}>
      <div className="panel-header">
        <span className="flex items-center gap-2">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-[color:var(--signal)] animate-pulse" />
          {id ? <span>{id}</span> : null}
        </span>
        {status ? <span className="text-foreground/70">{status}</span> : null}
      </div>
      {title ? (
        <div className="px-4 pt-4">
          <h3 className="font-display text-xl italic">{title}</h3>
          <div className="etched mt-2 h-1" />
        </div>
      ) : null}
      <div className="p-4">{children}</div>
    </div>
  );
}
