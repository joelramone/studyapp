import { DocumentRecord, ProcessRecord } from "@/lib/types";

export interface StorageProvider {
  createDocument(record: DocumentRecord): Promise<void>;
  listDocuments(): Promise<DocumentRecord[]>;
  getDocument(id: string): Promise<DocumentRecord | null>;
  saveProcess(record: ProcessRecord): Promise<void>;
  getProcess(docId: string, chapterId: string): Promise<ProcessRecord | null>;
}

class InMemoryStorage implements StorageProvider {
  private readonly documents = new Map<string, DocumentRecord>();
  private readonly process = new Map<string, ProcessRecord>();

  async createDocument(record: DocumentRecord): Promise<void> {
    this.documents.set(record.id, record);
  }

  async listDocuments(): Promise<DocumentRecord[]> {
    return Array.from(this.documents.values()).sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }

  async getDocument(id: string): Promise<DocumentRecord | null> {
    return this.documents.get(id) ?? null;
  }

  async saveProcess(record: ProcessRecord): Promise<void> {
    this.process.set(`${record.docId}:${record.chapterId}`, record);
  }

  async getProcess(docId: string, chapterId: string): Promise<ProcessRecord | null> {
    return this.process.get(`${docId}:${chapterId}`) ?? null;
  }
}

const globalStore = globalThis as unknown as { studybrainStorage?: InMemoryStorage };

export const storage: StorageProvider = globalStore.studybrainStorage ?? new InMemoryStorage();
if (!globalStore.studybrainStorage) {
  globalStore.studybrainStorage = storage as InMemoryStorage;
}
