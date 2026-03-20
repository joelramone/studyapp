import { lookup } from "node:dns/promises";
import { NextResponse } from "next/server";
import { handleApiError } from "@/app/api/_utils";
import { HealthStatus } from "@/lib/types";

export async function GET(): Promise<NextResponse> {
  try {
    const details: string[] = [];
    const apiKeyPresent = Boolean(process.env.OPENAI_API_KEY);
    if (!apiKeyPresent) {
      details.push("OPENAI_API_KEY ausente.");
    }

    let dnsOk = false;
    try {
      await lookup("api.openai.com");
      dnsOk = true;
    } catch {
      details.push("DNS no pudo resolver api.openai.com.");
    }

    let httpOk = false;
    try {
      const res = await fetch("https://api.openai.com/v1/models", {
        method: "GET",
        headers: apiKeyPresent
          ? {
              Authorization: `Bearer ${process.env.OPENAI_API_KEY}`
            }
          : undefined
      });
      httpOk = res.status === 200 || res.status === 401;
      if (!httpOk) {
        details.push(`HTTP OpenAI devolvió ${res.status}.`);
      }
    } catch {
      details.push("Fallo de conectividad HTTP con OpenAI.");
    }

    const apiOk = apiKeyPresent && dnsOk && httpOk;
    const health: HealthStatus = { apiKeyPresent, dnsOk, httpOk, apiOk, details };

    return NextResponse.json({ health });
  } catch (error: unknown) {
    return handleApiError(error);
  }
}
