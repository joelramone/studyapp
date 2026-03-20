import { NextResponse } from "next/server";
import { ApiError } from "@/lib/errors";

export function handleApiError(error: unknown): NextResponse {
  if (error instanceof ApiError) {
    return NextResponse.json({ error: error.toShape() }, { status: error.status });
  }

  const message = error instanceof Error ? error.message : "Error inesperado";
  return NextResponse.json(
    {
      error: {
        code: "UNEXPECTED_ERROR",
        message: "Ocurrió un error inesperado.",
        details: message
      }
    },
    { status: 500 }
  );
}
