import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.chunker import chunk_pages  # noqa: E402


def test_chunking_produces_chunks():
    pages = [
        {"page": 1, "text": " ".join(["word"] * 400)},
        {"page": 2, "text": " ".join(["word"] * 400)},
    ]
    chunks = chunk_pages(pages, chunk_size_tokens=200, overlap_tokens=20)
    assert len(chunks) > 1
    for c in chunks:
        assert "text" in c and "page" in c and "chunk_index" in c
        assert c["page"] in (1, 2)


def test_chunk_overlap_smaller_than_chunk_size():
    pages = [{"page": 1, "text": " ".join([f"w{i}" for i in range(1000)])}]
    chunks = chunk_pages(pages, chunk_size_tokens=100, overlap_tokens=20)
    # consecutive chunks should share some words due to overlap
    if len(chunks) > 1:
        first_words = set(chunks[0]["text"].split())
        second_words = set(chunks[1]["text"].split())
        assert first_words & second_words
