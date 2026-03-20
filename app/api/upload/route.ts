import { NextResponse } from "next/server";
import pdfParse from "pdf-parse";
import { handleApiError } from "@/app/api/_utils";
import { ApiError } from "@/lib/errors";
import { createDocument } from "@/lib/pipeline";
import { storage } from "@/lib/storage";

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const form = await request.formData();
    const title = String(form.get("title") ?? "PDF");
    const file = form.get("file");

    if (!(file instanceof File)) {
      throw new ApiError(400, "MISSING_FILE", "Debes adjuntar un archivo PDF.");
    }

    const arrayBuffer = await file.arrayBuffer();
    const text = (await pdfParse(Buffer.from(arrayBuffer))).text.trim();

    if (!text) {
      throw new ApiError(400, "EMPTY_PDF", "No se pudo extraer texto del PDF.");
    }

    const record = createDocument({ title, sourceType: "pdf", content: text });
    await storage.createDocument(record);

    return NextResponse.json({ document: record }, { status: 201 });
  } catch (error: unknown) {
    return handleApiError(error);
  }
}
