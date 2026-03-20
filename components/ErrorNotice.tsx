import { ReactNode } from "react";

export function ErrorNotice({ message }: { message: string }): ReactNode {
  return <div className="rounded-lg border border-red-500/50 bg-red-950/50 p-3 text-sm text-red-200">{message}</div>;
}
