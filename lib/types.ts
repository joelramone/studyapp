export type OutputType = "summary" | "concepts" | "architecture" | "mindmap" | "flashcards" | "exam";

export interface Chapter {
  id: string;
  title: string;
  content: string;
  chunkCount: number;
}

export interface DocumentRecord {
  id: string;
  title: string;
  sourceType: "notes" | "pdf";
  rawContent: string;
  chapters: Chapter[];
  createdAt: string;
  updatedAt: string;
}

export interface ResultBundle {
  summary: string;
  concepts: string;
  architecture: string;
  mindmap: string;
  flashcards: string;
  exam: string;
}

export interface ProcessRecord {
  docId: string;
  chapterId: string;
  outputs: Partial<ResultBundle>;
  updatedAt: string;
}

export interface HealthStatus {
  apiKeyPresent: boolean;
  dnsOk: boolean;
  httpOk: boolean;
  apiOk: boolean;
  details: string[];
}

export interface ApiErrorShape {
  code: string;
  message: string;
  details?: string;
}
