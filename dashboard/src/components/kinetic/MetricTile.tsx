import * as React from "react";
import { motion } from "framer-motion";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Props {
  id: string;
  label: string;
  value: React.ReactNode;
  suffix?: string;
  accent?: "primary" | "accent" | "destructive" | "foreground";
  icon?: React.ReactNode;
}

const accentMap = {
  primary: "text-primary",
  accent: "text-accent",
  destructive: "text-destructive",
  foreground: "text-foreground",
};

export function MetricTile({ id, label, value, suffix, accent = "primary", icon }: Props) {
  return (
    <div className="panel">
      <div className="panel-header">
        <span className="flex items-center gap-2">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-[color:var(--signal)] animate-pulse" />
          METRIC_ID: {id}
        </span>
        <span className="opacity-70">{icon}</span>
      </div>
      <div className="px-4 pt-3 pb-4">
        <p className="font-mono-ui text-[10px] uppercase tracking-widest text-muted-foreground">
          {label}
        </p>
        <motion.p
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className={cn("font-display italic text-5xl mt-2 tabular-nums", accentMap[accent])}
        >
          {value}
          {suffix ? <span className="text-3xl">{suffix}</span> : null}
        </motion.p>
        <div className="etched mt-3 h-1" />
      </div>
    </div>
  );
}
