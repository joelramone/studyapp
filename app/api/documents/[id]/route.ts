import { NextResponse } from "next/server";
import { handleApiError } from "@/app/api/_utils";
import { ApiError } from "@/lib/errors";
import { storage } from "@/lib/storage";

export async function GET(_: Request, context: { params: Promise<{ id: string }> }): Promise<NextResponse> {
  try {
    const { id } = await context.params;
    const document = await storage.getDocument(id);
    if (!document) {
      throw new ApiError(404, "DOCUMENT_NOT_FOUND", "Documento no encontrado.");
    }

    return NextResponse.json({ document });
  } catch (error: unknown) {
    return handleApiError(error);
  }
}
