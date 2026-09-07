"""
Splits page text into overlapping chunks, preserving the page number
each chunk originated from.

Token counts here are approximated by word count (roughly 0.75 words
per token for English text) to avoid pulling in a tokenizer dependency.
This is precise enough for chunk-sizing purposes.
"""
from config import CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS

WORDS_PER_TOKEN = 0.75  # approximation


def _words_for_tokens(tokens):
    return max(1, int(tokens * WORDS_PER_TOKEN))


def chunk_pages(pages, chunk_size_tokens=None, overlap_tokens=None):
    """
    pages: list of {"page": int, "text": str}
    Returns: list of {"page": int, "text": str, "chunk_index": int}
    Chunking is done by concatenating page text in order and sliding a
    word-window across it, so a chunk that spans a page boundary is
    tagged with its *starting* page.
    """
    chunk_size_tokens = chunk_size_tokens or CHUNK_SIZE_TOKENS
    overlap_tokens = overlap_tokens or CHUNK_OVERLAP_TOKENS

    chunk_size_words = _words_for_tokens(chunk_size_tokens)
    overlap_words = _words_for_tokens(overlap_tokens)
    step = max(1, chunk_size_words - overlap_words)

    # Flatten into a list of (word, page_number) tuples so we can track
    # which page each word came from.
    words_with_page = []
    for p in pages:
        for w in p["text"].split():
            words_with_page.append((w, p["page"]))

    chunks = []
    i = 0
    chunk_index = 0
    n = len(words_with_page)
    while i < n:
        window = words_with_page[i:i + chunk_size_words]
        if not window:
            break
        text = " ".join(w for w, _ in window)
        start_page = window[0][1]
        chunks.append({
            "chunk_index": chunk_index,
            "page": start_page,
            "text": text,
        })
        chunk_index += 1
        if i + chunk_size_words >= n:
            break
        i += step

    return chunks
