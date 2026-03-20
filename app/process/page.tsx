"use client";

import { FormEvent, useEffect, useState } from "react";
import { ErrorNotice } from "@/components/ErrorNotice";
import { DocumentRecord, OutputType } from "@/lib/types";

const options: { value: OutputType; label: string }[] = [
  { value: "summary", label: "Summary" },
  { value: "concepts", label: "Concepts" },
  { value: "architecture", label: "Architecture" },
  { value: "mindmap", label: "Mindmap" },
  { value: "flashcards", label: "Flashcards" },
  { value: "exam", label: "Exam" }
];

export default function ProcessPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [docId, setDocId] = useState("");
  const [chapterId, setChapterId] = useState("");
  const [outputs, setOutputs] = useState<OutputType[]>(["summary", "concepts"]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      const res = await fetch("/api/documents");
      const data = (await res.json()) as { documents: DocumentRecord[] };
      setDocuments(data.documents ?? []);
      const firstDoc = data.documents?.[0];
      if (firstDoc) {
        setDocId(firstDoc.id);
        setChapterId(firstDoc.chapters[0]?.id ?? "");
      }
    };
    void load();
  }, []);

  const chapters = documents.find((doc) => doc.id === docId)?.chapters ?? [];

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const res = await fetch("/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ docId, chapterId, outputs })
      });
      const data = (await res.json()) as { process?: { chapterId: string }; error?: { message?: string } };
      if (!res.ok) {
        throw new Error(data.error?.message ?? "No se pudo procesar el capítulo");
      }

      setMessage(`Procesamiento completado para capítulo ${data.process?.chapterId}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error de procesamiento");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="space-y-4 rounded-xl border border-slate-800 bg-slate-900 p-4">
      <h2 className="font-semibold">Ejecutar agentes IA</h2>

      <label className="block text-sm">
        Documento
        <select value={docId} onChange={(event) => setDocId(event.target.value)} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2">
          {documents.map((doc) => (
            <option key={doc.id} value={doc.id}>
              {doc.title}
            </option>
          ))}
        </select>
      </label>

      <label className="block text-sm">
        Capítulo
        <select value={chapterId} onChange={(event) => setChapterId(event.target.value)} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2">
          {chapters.map((ch) => (
            <option key={ch.id} value={ch.id}>
              {ch.title}
            </option>
          ))}
        </select>
      </label>

      <fieldset className="space-y-2">
        <legend className="text-sm">Outputs</legend>
        {options.map((option) => (
          <label key={option.value} className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={outputs.includes(option.value)}
              onChange={(event) => {
                if (event.target.checked) {
                  setOutputs((prev) => Array.from(new Set([...prev, option.value])));
                } else {
                  setOutputs((prev) => prev.filter((value) => value !== option.value));
                }
              }}
            />
            {option.label}
          </label>
        ))}
      </fieldset>

      <button disabled={loading} className="w-full rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold disabled:opacity-60">
        {loading ? "Procesando agentes..." : "Ejecutar"}
      </button>

      {error && <ErrorNotice message={error} />}
      {message && <div className="rounded-lg border border-emerald-500/40 bg-emerald-950/40 p-3 text-sm text-emerald-200">{message}</div>}
    </form>
  );
}
