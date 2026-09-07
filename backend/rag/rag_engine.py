"""
Orchestrates the full RAG flow: process a new document into an index,
and answer a question by retrieving relevant chunks + calling the LLM.

This module has no Flask dependency so it can be exercised directly
from a standalone script (see scripts/test_rag.py).
"""
from config import TOP_K, MAX_HISTORY_TURNS
from rag.pdf_processor import extract_or_raise
from rag.chunker import chunk_pages
from rag.embeddings import embed_chunks, embed_query
from rag.vector_store import build_and_save_index, search, search_multiple
from llm.gemini_client import generate_answer


def process_document(document_id, file_path):
    """
    Full ingestion pipeline for a newly uploaded PDF:
    extract -> chunk -> embed -> build FAISS index -> persist.

    Returns (num_pages, num_chunks, index_path).
    """
    pages, num_pages = extract_or_raise(file_path)
    chunks = chunk_pages(pages)
    chunk_texts = [c["text"] for c in chunks]
    embeddings = embed_chunks(chunk_texts)
    index_path = build_and_save_index(document_id, chunks, embeddings)
    return num_pages, len(chunks), index_path


def _format_context(chunks, filename_lookup=None):
    """filename_lookup: optional dict of document_id -> filename, used
    when chunks come from multiple documents."""
    lines = []
    for c in chunks:
        doc_label = ""
        if filename_lookup and "document_id" in c:
            doc_label = f"{filename_lookup.get(c['document_id'], 'Document')} - "
        lines.append(f"[{doc_label}Page {c['page']}]\n{c['text']}")
    return "\n\n".join(lines) if lines else "(no relevant context found)"


def _format_history(history_messages):
    if not history_messages:
        return "(no prior conversation)"
    recent = history_messages[-(MAX_HISTORY_TURNS * 2):]
    lines = []
    for m in recent:
        role = "User" if m["role"] == "user" else "AI"
        lines.append(f"{role}: {m['content']}")
    return "\n".join(lines)


def answer_question(question, document_id=None, document_ids=None,
                     history_messages=None, filename_lookup=None, top_k=None):
    """
    document_id: single-document mode
    document_ids: multi-document mode (list) - takes precedence if provided
    Returns: {"answer": str, "sources": [{"document": str|None, "page": int}]}
    """
    top_k = top_k or TOP_K
    query_embedding = embed_query(question)

    if document_ids:
        chunks = search_multiple(document_ids, query_embedding, top_k=top_k)
    elif document_id is not None:
        chunks = search(document_id, query_embedding, top_k=top_k)
    else:
        chunks = []

    context_text = _format_context(chunks, filename_lookup)
    history_text = _format_history(history_messages or [])

    answer_text = generate_answer(context_text, history_text, question)

    sources = []
    seen = set()
    for c in chunks:
        doc_name = None
        if filename_lookup and "document_id" in c:
            doc_name = filename_lookup.get(c["document_id"])
        key = (doc_name, c["page"])
        if key not in seen:
            seen.add(key)
            sources.append({"document": doc_name, "page": c["page"]})

    return {"answer": answer_text, "sources": sources}
