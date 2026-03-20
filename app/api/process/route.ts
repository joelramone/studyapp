import { NextResponse } from "next/server";
import { handleApiError } from "@/app/api/_utils";
import { processChapter } from "@/lib/pipeline";
import { OutputType } from "@/lib/types";

const allowed: OutputType[] = ["summary", "concepts", "architecture", "mindmap", "flashcards", "exam"];

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body = (await request.json()) as { docId: string; chapterId: string; outputs: OutputType[] };
    const outputs = body.outputs.filter((item): item is OutputType => allowed.includes(item));
    const process = await processChapter(body.docId, body.chapterId, outputs);
    return NextResponse.json({ process });
  } catch (error: unknown) {
    return handleApiError(error);
  }
}
