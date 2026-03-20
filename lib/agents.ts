import { runOpenAIJson } from "@/lib/openai";
import { OutputType, ResultBundle } from "@/lib/types";

interface AgentInput {
  title: string;
  content: string;
}

async function conceptAgent(input: AgentInput): Promise<Pick<ResultBundle, "summary" | "concepts">> {
  const prompt = `Analiza el capítulo "${input.title}" y devuelve:
1) resumen ejecutivo
2) conceptos clave con definición y relaciones

Contenido:\n${input.content}`;

  const schema = `JSON con estructura:
{
  "summary": "string",
  "concepts": "markdown con lista de conceptos, definiciones y relaciones"
}`;

  const raw = await runOpenAIJson(prompt, schema);
  const parsed = JSON.parse(raw) as { summary: string; concepts: string };
  return { summary: parsed.summary, concepts: parsed.concepts };
}

async function architectureAgent(input: AgentInput): Promise<Pick<ResultBundle, "architecture">> {
  const prompt = `Genera arquitectura de aprendizaje para el capítulo "${input.title}" incluyendo:
- componentes
- relaciones
- flujo paso a paso
- errores comunes

Contenido:\n${input.content}`;

  const schema = `JSON con estructura:
{
  "architecture": "markdown estructurado"
}`;

  const raw = await runOpenAIJson(prompt, schema);
  const parsed = JSON.parse(raw) as { architecture: string };
  return { architecture: parsed.architecture };
}

async function mindmapAgent(input: AgentInput): Promise<Pick<ResultBundle, "mindmap">> {
  const prompt = `Convierte el capítulo "${input.title}" en un mindmap jerárquico en markdown.`;
  const schema = `JSON con estructura:
{
  "mindmap": "markdown jerárquico con bullets indentados"
}`;

  const raw = await runOpenAIJson(`${prompt}\n\n${input.content}`, schema);
  const parsed = JSON.parse(raw) as { mindmap: string };
  return { mindmap: parsed.mindmap };
}

async function flashcardAgent(input: AgentInput): Promise<Pick<ResultBundle, "flashcards">> {
  const prompt = `Genera flashcards para Anki del capítulo "${input.title}".`;
  const schema = `JSON con estructura:
{
  "flashcards": "CSV con encabezado front,back,tags,difficulty"
}`;

  const raw = await runOpenAIJson(`${prompt}\n\n${input.content}`, schema);
  const parsed = JSON.parse(raw) as { flashcards: string };
  return { flashcards: parsed.flashcards };
}

async function examAgent(input: AgentInput): Promise<Pick<ResultBundle, "exam">> {
  const prompt = `Crea examen del capítulo "${input.title}" con:
- preguntas multiple choice
- short answer
- scenario based`;
  const schema = `JSON con estructura:
{
  "exam": "markdown con secciones y respuestas sugeridas"
}`;

  const raw = await runOpenAIJson(`${prompt}\n\n${input.content}`, schema);
  const parsed = JSON.parse(raw) as { exam: string };
  return { exam: parsed.exam };
}

export async function runAgents(input: AgentInput, outputs: OutputType[]): Promise<Partial<ResultBundle>> {
  const result: Partial<ResultBundle> = {};

  if (outputs.includes("summary") || outputs.includes("concepts")) {
    const concept = await conceptAgent(input);
    if (outputs.includes("summary")) {
      result.summary = concept.summary;
    }
    if (outputs.includes("concepts")) {
      result.concepts = concept.concepts;
    }
  }

  if (outputs.includes("architecture")) {
    Object.assign(result, await architectureAgent(input));
  }
  if (outputs.includes("mindmap")) {
    Object.assign(result, await mindmapAgent(input));
  }
  if (outputs.includes("flashcards")) {
    Object.assign(result, await flashcardAgent(input));
  }
  if (outputs.includes("exam")) {
    Object.assign(result, await examAgent(input));
  }

  return result;
}
