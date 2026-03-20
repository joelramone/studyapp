"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

const nav = [
  { href: "/", label: "Dashboard" },
  { href: "/upload", label: "Upload" },
  { href: "/documents", label: "Docs" },
  { href: "/process", label: "Process" },
  { href: "/health", label: "Health" }
];

export function AppShell({ children }: { children: ReactNode }): ReactNode {
  const pathname = usePathname();

  return (
    <div className="mx-auto min-h-screen max-w-md bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-950/95 px-4 py-3 backdrop-blur">
        <h1 className="text-lg font-semibold">StudyBrain Web</h1>
        <p className="text-xs text-slate-400">Mobile-first IA study workflow</p>
      </header>

      <main className="px-4 pb-24 pt-4">{children}</main>

      <nav className="fixed bottom-0 left-0 right-0 mx-auto flex max-w-md border-t border-slate-800 bg-slate-950 p-2">
        {nav.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex-1 rounded-md px-2 py-2 text-center text-xs font-medium ${
                active ? "bg-indigo-600 text-white" : "text-slate-300"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
