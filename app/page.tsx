"use client";

import { useEffect, useState } from "react";
import { ErrorNotice } from "@/components/ErrorNotice";
import { LoadingBlock } from "@/components/LoadingBlock";
import { StatusCard } from "@/components/StatusCard";
import { DocumentRecord } from "@/lib/types";

export default function DashboardPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("/api/documents");
        const data = (await res.json()) as { documents: DocumentRecord[]; error?: { message?: string } };
        if (!res.ok) {
          throw new Error(data.error?.message ?? "No se pudo cargar dashboard");
        }
        setDocuments(data.documents);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Error cargando dashboard");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  const chapters = documents.reduce((acc, doc) => acc + doc.chapters.length, 0);

  return (
    <section className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <StatusCard title="Documentos" value={String(documents.length)} description="Ingestados en sesión" />
        <StatusCard title="Capítulos" value={String(chapters)} description="Detectados por heurística" />
      </div>

      {loading && <LoadingBlock label="Cargando documentos..." />}
      {error && <ErrorNotice message={error} />}

      <div className="space-y-2">
        {documents.map((doc) => (
          <article key={doc.id} className="rounded-xl border border-slate-800 bg-slate-900 p-3">
            <h2 className="font-medium">{doc.title}</h2>
            <p className="text-xs text-slate-400">{doc.sourceType.toUpperCase()} · {doc.chapters.length} capítulos</p>
          </article>
        ))}
      </div>
    </section>
  );
}
