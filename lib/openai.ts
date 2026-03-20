import OpenAI from "openai";
import { ApiError } from "@/lib/errors";

const model = "gpt-4.1-mini";

function getClient(): OpenAI {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new ApiError(500, "MISSING_API_KEY", "OPENAI_API_KEY no está configurada.");
  }

  return new OpenAI({ apiKey });
}

export async function runOpenAIJson(prompt: string, schemaDescription: string): Promise<string> {
  try {
    const client = getClient();

    const response = await client.responses.create({
      model,
      input: [
        {
          role: "system",
          content: [
            {
              type: "input_text",
              text: "Eres un asistente académico. Responde en español claro, estructurado y accionable."
            }
          ]
        },
        {
          role: "user",
          content: [
            {
              type: "input_text",
              text: `${prompt}\n\nFormato requerido:\n${schemaDescription}`
            }
          ]
        }
      ],
      temperature: 0.2
    });

    const text = response.output_text?.trim();
    if (!text) {
      throw new ApiError(502, "EMPTY_MODEL_OUTPUT", "El modelo devolvió una respuesta vacía.");
    }

    return text;
  } catch (error: unknown) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error && typeof error === "object" && "code" in error) {
      const code = String((error as { code?: string }).code || "OPENAI_ERROR");
      if (code.includes("ENOTFOUND") || code.includes("EAI_AGAIN")) {
        throw new ApiError(503, "DNS_ERROR", "Fallo de DNS al conectar con OpenAI.", code);
      }
    }

    const message = error instanceof Error ? error.message : "Error desconocido llamando OpenAI.";
    throw new ApiError(502, "OPENAI_REQUEST_FAILED", "No se pudo completar la solicitud a OpenAI.", message);
  }
}
