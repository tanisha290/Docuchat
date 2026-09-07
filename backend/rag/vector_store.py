"""
FAISS-backed vector store: one index per document, persisted to disk
alongside a metadata sidecar file (chunk text + page number per vector)
so the index survives server restarts.
"""
import json
import os

import faiss
import numpy as np

from config import INDEX_DIR, EMBEDDING_DIM


def _index_path(document_id):
    return os.path.join(INDEX_DIR, f"{document_id}.index")


def _meta_path(document_id):
    return os.path.join(INDEX_DIR, f"{document_id}.meta.json")


def build_and_save_index(document_id, chunks, embeddings):
    """
    chunks: list of {"chunk_index", "page", "text"}
    embeddings: list[list[float]], same length/order as chunks
    """
    vectors = np.array(embeddings, dtype="float32")
    if vectors.ndim != 2 or vectors.shape[0] == 0:
        raise ValueError("No embeddings to index.")

    # Normalize for cosine similarity via inner product.
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(index, _index_path(document_id))
    with open(_meta_path(document_id), "w") as f:
        json.dump(chunks, f)

    return _index_path(document_id)


def load_index(document_id):
    idx_path = _index_path(document_id)
    meta_path = _meta_path(document_id)
    if not os.path.exists(idx_path) or not os.path.exists(meta_path):
        return None, None
    index = faiss.read_index(idx_path)
    with open(meta_path) as f:
        chunks = json.load(f)
    return index, chunks


def search(document_id, query_embedding, top_k=5):
    """Returns top_k chunks (each with a similarity score) for one document."""
    index, chunks = load_index(document_id)
    if index is None:
        return []

    query_vec = np.array([query_embedding], dtype="float32")
    faiss.normalize_L2(query_vec)
    scores, indices = index.search(query_vec, min(top_k, index.ntotal))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = dict(chunks[idx])
        chunk["score"] = float(score)
        results.append(chunk)
    return results


def search_multiple(document_ids, query_embedding, top_k=5):
    """Search across several documents and merge results by score (for
    the optional multi-document comparison mode)."""
    all_results = []
    for doc_id in document_ids:
        for chunk in search(doc_id, query_embedding, top_k=top_k):
            chunk["document_id"] = doc_id
            all_results.append(chunk)
    all_results.sort(key=lambda c: c["score"], reverse=True)
    return all_results[:top_k]


def delete_index(document_id):
    for path in (_index_path(document_id), _meta_path(document_id)):
        if os.path.exists(path):
            os.remove(path)
