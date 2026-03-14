from services.chunker import TextChunker


def test_chunker_overlapping_chunks() -> None:
    chunker = TextChunker(chunk_size=10, overlap=2)
    chunks = chunker.chunk("abcdefghijklmnopqrstuvwxyz")
    assert chunks
    assert chunks[0] == "abcdefghij"
    assert chunks[1].startswith("ij")
