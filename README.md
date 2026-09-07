# DocuChat — Conversational PDF RAG System

A conversational document QA system using RAG where users upload PDFs and ask multi-turn questions about their contents. The system extracts and chunks the document, generates embeddings, stores them in FAISS, retrieves the most relevant chunks per query, and provides that context plus conversation history to Gemini to generate grounded, cited answers.

## Architecture

```
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │   React UI  │
                    └──────┬──────┘
                           │ REST API
                           ▼
                    ┌─────────────┐
                    │    Flask    │
                    │   Backend   │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        PDF Processor    SQLite        RAG Engine
             │                          │
             ▼                          ▼
          Chunks               Embeddings + FAISS
             │                          │
             └──────────┬───────────────┘
                         ▼
                  Gemini LLM (generation)
                         │
                         ▼
                   Final Answer + Sources
```

The RAG pipeline (`backend/rag/`) has no Flask dependency, so it can be run and tested standalone via `backend/scripts/test_rag.py` before ever touching the API.

## Project layout

```
docuchat/
├── backend/
│   ├── app.py                # Flask app entrypoint
│   ├── config.py              # env vars, tuning constants
│   ├── models.py               # SQLAlchemy models
│   ├── database.py             # DB init
│   ├── routes/                 # documents, conversations, chat endpoints
│   ├── rag/                    # pdf_processor, chunker, embeddings, vector_store, rag_engine
│   ├── llm/                    # gemini_client.py
│   ├── scripts/test_rag.py     # standalone RAG smoke test
│   ├── tests/                  # pytest suite
│   ├── storage/                # uploaded PDFs + FAISS indexes + sqlite db (gitignored)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/         # DocumentList, ChatWindow, MessageBubble, UploadButton
    │   ├── api/client.js        # REST client
    │   ├── App.jsx
    │   └── main.jsx
    └── package.json
```

## Setup

### 1. Get a Gemini API key

Create one at https://aistudio.google.com/app/apikey.

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your GEMINI_API_KEY

python app.py
```

The API runs at `http://localhost:5000`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI runs at `http://localhost:5173` and proxies `/api` requests to the Flask backend (see `vite.config.js`).

### 4. (Optional) Test the RAG pipeline standalone first

Before running the full app, you can sanity-check the pipeline directly:

```bash
cd backend
python scripts/test_rag.py path/to/some.pdf "What is this document about?"
```

This exercises extraction → chunking → embedding → FAISS indexing → retrieval → Gemini generation, without needing Flask or the database.

## API reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/documents/upload` | Upload a PDF (multipart `file` field); triggers processing |
| GET | `/api/documents` | List all uploaded documents |
| DELETE | `/api/documents/<id>` | Delete a document, its file, and its index |
| POST | `/api/conversations` | Create a conversation (optional `document_id`) |
| GET | `/api/conversations` | List conversations |
| GET | `/api/conversations/<id>` | Get a conversation with its messages |
| POST | `/api/conversations/<id>/messages` | Send a user message, get an answer + sources |
| GET | `/api/conversations/<id>/messages` | Get full message history |
| GET | `/api/health` | Health check |

Chat response shape:

```json
{
  "answer": "Students with a CGPA of at least 7.0 and no active backlogs are eligible.",
  "sources": [
    {"document": "Placement Policy.pdf", "page": 4},
    {"document": "Placement Policy.pdf", "page": 7}
  ]
}
```

## Running tests

```bash
cd backend
pip install pytest
pytest tests/
```

`tests/test_chunker.py` exercises the chunking logic directly (no external calls). `tests/test_api.py` exercises routing, validation, and error handling via Flask's test client against an in-memory SQLite database (it does not call the real Gemini API).

## Known limitations & possible next steps

- **Scanned PDFs**: documents with no extractable text (image-only scans) are rejected at upload time. Adding OCR (e.g. Tesseract) would extend support to these.
- **Multi-document comparison**: the backend supports querying across multiple documents (`rag/vector_store.search_multiple`) and the chat endpoint accepts an optional `document_ids` list, but the current frontend only wires up single-document conversations. Extending the UI to let a user select several documents at once is a natural next step.
- **Streaming responses**: answers are currently returned in one shot. Streaming the Gemini response token-by-token to the frontend would make longer answers feel faster.
- **Chat history sidebar**: conversations are persisted and listable via the API, but the frontend doesn't yet expose a "previous conversations" list in the UI.
- **Deployment**: SQLite and local FAISS index files work well for a single-instance deployment (e.g. Render, Railway, Fly.io) as long as they're placed on a persistent volume. For multi-instance scaling, moving to a managed Postgres database and a hosted vector store (e.g. pgvector) would be the natural upgrade path.
