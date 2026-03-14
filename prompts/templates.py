SUMMARY_PROMPT = """You are a technical study assistant. Summarize the chapter in concise markdown with key points and practical notes."""

CONCEPT_PROMPT = """Extract key concepts from the chapter. Return strict JSON list with fields: name, description, tags."""

MINDMAP_PROMPT = """Build a markdown mindmap using nested bullet points from the chapter content."""

FLASHCARD_PROMPT = """Create study flashcards in CSV with columns: question,answer,difficulty."""

EXAM_PROMPT = """Generate 5 challenging exam-style questions in markdown with short expected answers."""
