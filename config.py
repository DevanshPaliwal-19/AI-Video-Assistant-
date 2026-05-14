"""
config.py — Centralised configuration for AI Video Assistant.
All settings come from environment variables with safe defaults.
Never hardcode paths or secrets anywhere else in the codebase.
"""

import os
from pathlib import Path

# ── Project root ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.resolve()

# ── Directories ───────────────────────────────────────────────────────────────
DOWNLOAD_DIR = ROOT_DIR / os.getenv("DOWNLOAD_DIR", "downloads")
VECTOR_DB_DIR = ROOT_DIR / os.getenv("VECTOR_DB_DIR", "vector_db")

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# ── Whisper ───────────────────────────────────────────────────────────────────
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")          # tiny/base/small/medium/large
AUDIO_CHUNK_MINUTES = int(os.getenv("AUDIO_CHUNK_MINUTES", "10"))
AUDIO_SAMPLE_RATE = 16_000                                   # Hz — Whisper expects 16 kHz

# ── Mistral LLM ───────────────────────────────────────────────────────────────
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
LLM_TEMPERATURE_EXTRACT = float(os.getenv("LLM_TEMPERATURE_EXTRACT", "0.2"))
LLM_TEMPERATURE_SUMMARIZE = float(os.getenv("LLM_TEMPERATURE_SUMMARIZE", "0.3"))
LLM_TEMPERATURE_RAG = float(os.getenv("LLM_TEMPERATURE_RAG", "0.3"))

# ── Embeddings ────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "meeting_transcript")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "4"))

# ── Text splitting ────────────────────────────────────────────────────────────
SUMMARIZE_CHUNK_SIZE = int(os.getenv("SUMMARIZE_CHUNK_SIZE", "3000"))
SUMMARIZE_CHUNK_OVERLAP = int(os.getenv("SUMMARIZE_CHUNK_OVERLAP", "200"))
VECTOR_CHUNK_SIZE = int(os.getenv("VECTOR_CHUNK_SIZE", "5000"))
VECTOR_CHUNK_OVERLAP = int(os.getenv("VECTOR_CHUNK_OVERLAP", "100"))

# ── Supported languages ───────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = ["english", "hinglish", "hindi", "spanish", "french", "german", "japanese", "portuguese"]

# ── FFmpeg ────────────────────────────────────────────────────────────────────
# Optional: override only if ffmpeg is not on PATH (e.g. custom Windows install)
FFMPEG_LOCATION = os.getenv("FFMPEG_LOCATION", "")   # empty = use system PATH


def validate_env() -> list[str]:
    """Return list of missing required env vars. Empty list = all good."""
    errors = []
    if not MISTRAL_API_KEY:
        errors.append("MISTRAL_API_KEY is not set")
    return errors
