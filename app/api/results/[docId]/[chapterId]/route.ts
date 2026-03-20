import { NextResponse } from "next/server";
import { handleApiError } from "@/app/api/_utils";
import { ApiError } from "@/lib/errors";
import { storage } from "@/lib/storage";

export async function GET(
  _: Request,
  context: { params: Promise<{ docId: string; chapterId: string }> }
): Promise<NextResponse> {
  try {
    const { docId, chapterId } = await context.params;
    const process = await storage.getProcess(docId, chapterId);
    if (!process) {
      throw new ApiError(404, "RESULT_NOT_FOUND", "No existen resultados para ese capítulo.");
    }

    return NextResponse.json({ process });
  } catch (error: unknown) {
    return handleApiError(error);
  }
}
