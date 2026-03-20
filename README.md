# StudyBrain Web

Aplicación mobile-first con Next.js para cargar notas/PDF, detectar capítulos, ejecutar agentes IA y generar materiales de estudio por capítulo.

## Stack

- Next.js App Router + TypeScript
- Tailwind CSS
- Route Handlers (`/app/api/*`)
- OpenAI Responses API
- Almacenamiento en memoria (interfaz desacoplada para migrar a Blob/S3/DB)

## Requisitos

- Node.js 20+
- npm 10+
- `OPENAI_API_KEY`

## Instalación

```bash
npm install
cp .env.example .env.local
```

Completa `.env.local`:

```bash
OPENAI_API_KEY=tu_api_key
```

## Nota de seguridad

- El proyecto fija `next@15.2.6` (parche de seguridad recomendado para la línea 15.2.x).

## Desarrollo local

```bash
npm run dev
```

Abrir `http://localhost:3000`.

## Build de producción

```bash
npm run build
npm run start
```

## Deploy en Vercel

1. Importa este repo en Vercel.
2. Define variable de entorno: `OPENAI_API_KEY`.
3. Deploy.

La app es compatible con entorno serverless de Vercel.

## Endpoints

- `POST /api/upload`
- `POST /api/notes`
- `GET /api/documents`
- `GET /api/documents/[id]`
- `POST /api/process`
- `GET /api/results/[docId]/[chapterId]`
- `GET /api/health`

## Flujo funcional

1. Cargar PDF o notas.
2. Detección heurística de capítulos.
3. Orquestación de agentes IA por capítulo.
4. Persistencia temporal de outputs estructurados.
5. Visualización por tabs (Summary, Concepts, Architecture, Mindmap, Flashcards, Exam).

## PWA

Incluye `app/manifest.ts` e íconos base para instalación en celular.
