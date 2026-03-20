"use client";

import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ErrorNotice } from "@/components/ErrorNotice";
import { LoadingBlock } from "@/components/LoadingBlock";
import { ResultBundle } from "@/lib/types";

const tabs: { key: keyof ResultBundle; label: string }[] = [
  { key: "summary", label: "Summary" },
  { key: "concepts", label: "Concepts" },
  { key: "architecture", label: "Architecture" },
  { key: "mindmap", label: "Mindmap" },
  { key: "flashcards", label: "Flashcards" },
  { key: "exam", label: "Exam" }
];

export default function ResultsPage() {
  const params = useParams<{ docId: string; chapterId: string }>();
  const [active, setActive] = useState<keyof ResultBundle>("summary");
  const [outputs, setOutputs] = useState<Partial<ResultBundle>>({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`/api/results/${params.docId}/${params.chapterId}`);
        const data = (await res.json()) as { process?: { outputs: Partial<ResultBundle> }; error?: { message?: string } };
        if (!res.ok) {
          throw new Error(data.error?.message ?? "No se pudieron cargar resultados");
        }
        setOutputs(data.process?.outputs ?? {});
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Error cargando resultados");
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [params.chapterId, params.docId]);

  const currentText = useMemo(() => outputs[active] ?? "Output no generado para esta pestaña.", [outputs, active]);

  return (
    <section className="space-y-3">
      <div className="grid grid-cols-3 gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActive(tab.key)}
            className={`rounded-lg border px-2 py-2 text-xs ${
              active === tab.key ? "border-indigo-500 bg-indigo-600" : "border-slate-700 bg-slate-900"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading && <LoadingBlock label="Cargando resultados..." />}
      {error && <ErrorNotice message={error} />}

      {!loading && !error && (
        <article className="whitespace-pre-wrap rounded-xl border border-slate-800 bg-slate-900 p-4 text-sm leading-6">{currentText}</article>
      )}
    </section>
  );
}
