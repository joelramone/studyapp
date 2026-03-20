import { NextResponse } from "next/server";
import { handleApiError } from "@/app/api/_utils";
import { createDocument } from "@/lib/pipeline";
import { storage } from "@/lib/storage";

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body = (await request.json()) as { title?: string; notes?: string };
    const record = createDocument({
      title: body.title ?? "Notas",
      sourceType: "notes",
      content: body.notes ?? ""
    });

    await storage.createDocument(record);
    return NextResponse.json({ document: record }, { status: 201 });
  } catch (error: unknown) {
    return handleApiError(error);
  }
}
