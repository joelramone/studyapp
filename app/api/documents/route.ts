import { NextResponse } from "next/server";
import { handleApiError } from "@/app/api/_utils";
import { storage } from "@/lib/storage";

export async function GET(): Promise<NextResponse> {
  try {
    const documents = await storage.listDocuments();
    return NextResponse.json({ documents });
  } catch (error: unknown) {
    return handleApiError(error);
  }
}
