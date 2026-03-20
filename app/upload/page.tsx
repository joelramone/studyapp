"use client";

import { FormEvent, useState } from "react";
import { ErrorNotice } from "@/components/ErrorNotice";

export default function UploadPage() {
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submitNotes = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const res = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, notes })
      });
      const data = (await res.json()) as { document?: { id: string }; error?: { message?: string } };
      if (!res.ok) {
        throw new Error(data.error?.message ?? "No se pudo crear el documento");
      }
      setMessage(`Documento creado: ${data.document?.id ?? "ok"}`);
      setNotes("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error al subir notas");
    } finally {
      setLoading(false);
    }
  };

  const submitPdf = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) {
      setError("Selecciona un archivo PDF.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const form = new FormData();
      form.set("title", title);
      form.set("file", file);

      const res = await fetch("/api/upload", { method: "POST", body: form });
      const data = (await res.json()) as { document?: { id: string }; error?: { message?: string } };
      if (!res.ok) {
        throw new Error(data.error?.message ?? "No se pudo subir PDF");
      }

      setMessage(`PDF cargado: ${data.document?.id ?? "ok"}`);
      setFile(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error al subir PDF");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-5">
      <form onSubmit={submitNotes} className="space-y-3 rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h2 className="font-medium">Pegar notas</h2>
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Título del documento"
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
        />
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="Pega tus notas aquí"
          rows={8}
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
        />
        <button disabled={loading} className="w-full rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold disabled:opacity-60">
          {loading ? "Procesando..." : "Crear desde notas"}
        </button>
      </form>

      <form onSubmit={submitPdf} className="space-y-3 rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h2 className="font-medium">Subir PDF</h2>
        <input
          type="file"
          accept="application/pdf"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          className="w-full text-sm"
        />
        <button disabled={loading} className="w-full rounded-lg bg-emerald-600 px-3 py-2 text-sm font-semibold disabled:opacity-60">
          {loading ? "Subiendo..." : "Subir PDF"}
        </button>
      </form>

      {error && <ErrorNotice message={error} />}
      {message && <div className="rounded-lg border border-emerald-500/40 bg-emerald-950/40 p-3 text-sm text-emerald-200">{message}</div>}
    </section>
  );
}
