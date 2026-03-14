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

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Ejecución

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
