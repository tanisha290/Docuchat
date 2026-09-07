import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- API keys ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# --- Models ---
GEMINI_EMBEDDING_MODEL = os.environ.get("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
GEMINI_GENERATION_MODEL = os.environ.get("GEMINI_GENERATION_MODEL", "gemini-3.6-flash")

# --- Storage paths ---
UPLOAD_DIR = os.path.join(BASE_DIR, "storage", "uploads")
INDEX_DIR = os.path.join(BASE_DIR, "storage", "indexes")
DATABASE_PATH = os.path.join(BASE_DIR, "storage", "docuchat.db")
DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# --- RAG tuning ---
CHUNK_SIZE_TOKENS = int(os.environ.get("CHUNK_SIZE_TOKENS", 700))
CHUNK_OVERLAP_TOKENS = int(os.environ.get("CHUNK_OVERLAP_TOKENS", 100))
TOP_K = int(os.environ.get("TOP_K", 5))
MAX_HISTORY_TURNS = int(os.environ.get("MAX_HISTORY_TURNS", 5))
EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", 768))  # gemini-embedding-001 supports 768/1536/3072

# --- Flask ---
MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 25))
ALLOWED_EXTENSIONS = {"pdf"}
