import { ReactNode } from "react";

export function LoadingBlock({ label }: { label: string }): ReactNode {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900 p-4 text-sm text-slate-300 animate-pulse">{label}</div>
  );
}
