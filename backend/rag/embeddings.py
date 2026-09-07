"""
Wraps Gemini's embedding API. All embedding calls (for document chunks
and for user questions) go through here so there is a single place to
change models, batching behavior, or add caching.
"""
import time
import google.generativeai as genai

from config import EMBEDDING_DIM, GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL

genai.configure(api_key=GEMINI_API_KEY)

BATCH_SIZE = 20
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2


def _embed_with_retry(text, task_type):
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            result = genai.embed_content(
                model=GEMINI_EMBEDDING_MODEL,
                content=text,
                task_type=task_type,
                output_dimensionality=EMBEDDING_DIM,
            )
            return result["embedding"]
        except Exception as e:  # noqa: BLE001 - we want to retry on any transient error
            last_err = e
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
    raise RuntimeError(f"Gemini embedding call failed after {MAX_RETRIES} attempts: {last_err}")


def embed_chunks(chunk_texts):
    """
    chunk_texts: list[str]
    Returns: list[list[float]], one embedding vector per input chunk.
    """
    embeddings = []
    for i in range(0, len(chunk_texts), BATCH_SIZE):
        batch = chunk_texts[i:i + BATCH_SIZE]
        for text in batch:
            embeddings.append(_embed_with_retry(text, task_type="retrieval_document"))
    return embeddings


def embed_query(query_text):
    """Returns a single embedding vector for a user question."""
    return _embed_with_retry(query_text, task_type="retrieval_query")
