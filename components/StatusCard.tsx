import { ReactNode } from "react";

export function StatusCard({ title, value, description }: { title: string; value: string; description: string }): ReactNode {
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900 p-4">
      <p className="text-xs uppercase text-slate-400">{title}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
      <p className="mt-1 text-xs text-slate-400">{description}</p>
    </article>
  );
}
