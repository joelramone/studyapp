"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ErrorNotice } from "@/components/ErrorNotice";
import { LoadingBlock } from "@/components/LoadingBlock";
import { DocumentRecord } from "@/lib/types";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("/api/documents");
        const data = (await res.json()) as { documents: DocumentRecord[]; error?: { message?: string } };
        if (!res.ok) {
          throw new Error(data.error?.message ?? "No se pudieron cargar documentos");
        }
        setDocuments(data.documents);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Error cargando documentos");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  return (
    <section className="space-y-3">
      {loading && <LoadingBlock label="Cargando lista de documentos..." />}
      {error && <ErrorNotice message={error} />}

      {documents.map((doc) => (
        <article key={doc.id} className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <h2 className="font-semibold">{doc.title}</h2>
          <p className="text-xs text-slate-400">{doc.id}</p>
          <div className="mt-3 space-y-2">
            {doc.chapters.map((ch) => (
              <Link
                key={ch.id}
                href={`/results/${doc.id}/${ch.id}`}
                className="block rounded-lg border border-slate-700 p-2 text-sm hover:border-indigo-400"
              >
                {ch.title} · chunks: {ch.chunkCount}
              </Link>
            ))}
          </div>
        </article>
      ))}
    </section>
  );
}
