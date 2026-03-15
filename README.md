# study_brain

`study_brain` es un proyecto Python para estudiar documentación técnica en PDF y generar material de aprendizaje por capítulo usando OpenAI API.

## Arquitectura

```text
study_brain/
├── app/                # Interfaz Streamlit
├── core/               # Configuración, modelos y orquestador
├── services/           # Lectura de PDF, división, chunking y storage
├── agents/             # Agentes de generación por tipo de artefacto
├── prompts/            # Prompts base para los agentes
├── data/               # Entrada local (PDFs)
├── output/             # Resultados por documento/capítulo
└── tests/              # Pruebas básicas
```

## Flujo

1. Subes un PDF en la GUI de Streamlit.
2. El archivo se guarda en `data/pdfs/`.
3. Se extrae texto con PyMuPDF.
4. Se divide por capítulos/secciones (o fallback por tamaño).
5. Por cada capítulo se generan:
   - `summary.md`
   - `concepts.json`
   - `mindmap.md`
   - `flashcards.csv`
   - `exam_questions.md`
6. Se guardan resultados en `output/<documento>/chapter_xx/`.

## Requisitos

- Python 3.11+
- OpenAI API Key (opcional para resultados reales; sin key se usa fallback local)

## Instalación

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Ejecución local

Ejecuta siempre desde la raíz del repo (`studyapp/`) con este comando exacto:

```bash
python -m streamlit run app/streamlit_app.py
```

Comando alternativo (equivalente):

```bash
streamlit run app/streamlit_app.py
```

## Variables de entorno

Ver `.env.example`:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `DATA_DIR`
- `OUTPUT_DIR`
- `LOG_LEVEL`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`

## Tests

```bash
pytest -q
```

## Modelos de dominio y contratos JSON

El dominio interno en `core/models.py` ahora define entidades Pydantic tipadas y listas para persistencia JSON:

- `Document`: documento fuente con estado, idioma, metadatos y capítulos.
- `Chapter`: capítulo normalizado con índice, contenido, resumen opcional y metadatos.
- `Chunk`: unidad de texto con span (`start_char`/`end_char`) y tipo de chunk.
- `AgentRun`: trazabilidad de ejecución de agentes (estado, tiempos, duración, error, metadata).
- `ConceptItem`: concepto con tags, aliases, prerequisitos y score de confianza.
- `ArchitectureComponent`: componente arquitectónico con responsabilidades, entradas/salidas y tecnologías.
- `Relationship`: relación dirigida entre componentes con tipo semántico.
- `Flashcard`: tarjeta exportable (frente/reverso, dificultad, tags, explicación).
- `ExamQuestion`: pregunta de examen con tipo (`multiple_choice`, `true_false`, `short_answer`) y validaciones.
- `MindmapNode`: nodo jerárquico de mapa mental con hijos recursivos.

Contratos de salida por agente en `core/schemas.py`:

- `ConceptAgentResponse`: JSON consistente para `Concept Agent`.
- `ArchitectureAgentResponse`: incluye `components`, `relationships` y `flow_steps` paso a paso.
- `FlashcardAgentResponse`: incluye `to_csv()` para exportación.
- `ExamAgentResponse`: soporta múltiples tipos de pregunta.
- `MindmapAgentResponse`: entrega estructura jerárquica (`root`) y representación markdown (`as_markdown()`).

Helpers de serialización (`core/models.py`):

- `to_pretty_json(model)`
- `dump_json_file(data, path)`
- `load_json_file(path)`

## Troubleshooting OpenAI (red/proxy/DNS)

Si la app muestra errores de conectividad (por ejemplo `APIConnectionError`, `getaddrinfo failed` o timeout), revisa:

1. **OPENAI_API_KEY**
   - Define una clave válida en `.env` con `OPENAI_API_KEY=...`.
   - Reinicia Streamlit después de cambiar variables de entorno.

2. **Proxy corporativo**
   - Configura variables estándar si tu red lo requiere: `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`.
   - Verifica que el proxy permita salida HTTPS a OpenAI.

3. **DNS**
   - Si aparece `getaddrinfo failed`, hay problema de resolución de nombres.
   - Revisa la configuración DNS del sistema o de tu VPN/red corporativa.

4. **Firewall / red saliente**
   - Confirma que no haya bloqueo de conexiones HTTPS salientes desde tu host/contenedor.
   - Permite tráfico hacia endpoints de OpenAI según políticas de tu organización.

5. **Timeouts de red**
   - Si hay latencia alta o cortes intermitentes, reintenta el procesamiento del capítulo.

La pantalla **Process** ahora ejecuta un health check de conectividad OpenAI y muestra mensajes accionables por categoría de error (DNS, conexión, timeout, autenticación).
