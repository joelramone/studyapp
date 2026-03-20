import { chunkText } from "@/lib/chunker";
import { Chapter } from "@/lib/types";

function normalizeTitle(raw: string, index: number): string {
  const clean = raw.replace(/^#+\s*/, "").replace(/^chapter\s*\d+[:.-]?\s*/i, "").trim();
  return clean || `Chapter ${index + 1}`;
}

export function detectChapters(rawContent: string): Chapter[] {
  const normalized = rawContent.replace(/\r\n/g, "\n").trim();
  if (!normalized) {
    return [];
  }

  const headingRegex = /(^#{1,3}\s+.+$)|(^chapter\s+\d+[:.-]?.+$)|(^\d+\.\s+[A-ZÁÉÍÓÚÑ].+$)/gim;
  const matches = Array.from(normalized.matchAll(headingRegex));

  if (matches.length < 2) {
    const single = normalized;
    return [
      {
        id: "ch-1",
        title: "General",
        content: single,
        chunkCount: chunkText(single).length
      }
    ];
  }

  const chapters: Chapter[] = [];

  for (let i = 0; i < matches.length; i += 1) {
    const current = matches[i];
    const start = current.index ?? 0;
    const next = matches[i + 1];
    const end = next?.index ?? normalized.length;
    const block = normalized.slice(start, end).trim();
    const firstLine = block.split("\n")[0] ?? `Chapter ${i + 1}`;

    if (block.length > 40) {
      chapters.push({
        id: `ch-${i + 1}`,
        title: normalizeTitle(firstLine, i),
        content: block,
        chunkCount: chunkText(block).length
      });
    }
  }

  if (chapters.length === 0) {
    return [
      {
        id: "ch-1",
        title: "General",
        content: normalized,
        chunkCount: chunkText(normalized).length
      }
    ];
  }

  return chapters;
}
