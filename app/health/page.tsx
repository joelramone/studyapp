"use client";

import { useEffect, useState } from "react";
import { ErrorNotice } from "@/components/ErrorNotice";
import { LoadingBlock } from "@/components/LoadingBlock";
import { HealthStatus } from "@/lib/types";

export default function HealthPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("/api/health");
        const data = (await res.json()) as { health?: HealthStatus; error?: { message?: string } };
        if (!res.ok) {
          throw new Error(data.error?.message ?? "No se pudo validar salud");
        }
        setHealth(data.health ?? null);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Error verificando health");
      }
    };

    void load();
  }, []);

  if (error) {
    return <ErrorNotice message={error} />;
  }

  if (!health) {
    return <LoadingBlock label="Ejecutando checks de API, DNS y conexión..." />;
  }

  return (
    <section className="space-y-3">
      <article className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-sm">
        <p>OPENAI_API_KEY: {health.apiKeyPresent ? "OK" : "FALTA"}</p>
        <p>DNS api.openai.com: {health.dnsOk ? "OK" : "ERROR"}</p>
        <p>HTTP OpenAI: {health.httpOk ? "OK" : "ERROR"}</p>
        <p>API General: {health.apiOk ? "OK" : "NO DISPONIBLE"}</p>
      </article>

      {health.details.length > 0 && (
        <article className="rounded-xl border border-amber-500/50 bg-amber-950/30 p-4 text-sm text-amber-100">
          <h2 className="font-semibold">Detalles</h2>
          <ul className="mt-2 list-disc space-y-1 pl-4">
            {health.details.map((detail) => (
              <li key={detail}>{detail}</li>
            ))}
          </ul>
        </article>
      )}
    </section>
  );
}
