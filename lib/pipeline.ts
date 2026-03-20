import { detectChapters } from "@/lib/chapter";
import { ApiError } from "@/lib/errors";
import { runAgents } from "@/lib/agents";
import { storage } from "@/lib/storage";
import { DocumentRecord, OutputType, ProcessRecord } from "@/lib/types";

export function createDocument(params: { title: string; sourceType: "notes" | "pdf"; content: string }): DocumentRecord {
  const cleanContent = params.content.trim();
  if (!cleanContent) {
    throw new ApiError(400, "EMPTY_CONTENT", "El contenido no puede estar vacío.");
  }

  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    title: params.title.trim() || "Documento sin título",
    sourceType: params.sourceType,
    rawContent: cleanContent,
    chapters: detectChapters(cleanContent),
    createdAt: now,
    updatedAt: now
  };
}

export async function processChapter(docId: string, chapterId: string, outputs: OutputType[]): Promise<ProcessRecord> {
  const document = await storage.getDocument(docId);
  if (!document) {
    throw new ApiError(404, "DOCUMENT_NOT_FOUND", "Documento no encontrado.");
  }

  const chapter = document.chapters.find((ch) => ch.id === chapterId);
  if (!chapter) {
    throw new ApiError(404, "CHAPTER_NOT_FOUND", "Capítulo no encontrado.");
  }

  if (outputs.length === 0) {
    throw new ApiError(400, "NO_OUTPUTS_SELECTED", "Selecciona al menos un output para procesar.");
  }

  const generated = await runAgents(
    {
      title: chapter.title,
      content: chapter.content
    },
    outputs
  );

  const record: ProcessRecord = {
    docId,
    chapterId,
    outputs: generated,
    updatedAt: new Date().toISOString()
  };

  await storage.saveProcess(record);
  return record;
}
