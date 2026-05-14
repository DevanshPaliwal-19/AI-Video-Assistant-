"""
core/transcriber.py — Whisper-based speech-to-text.

Fixes vs original:
- Language string mapped to Whisper language codes (hinglish → hi)
- translate flag derived from language, not passed from caller
- Model singleton uses threading lock for safety
- Chunk paths now accept Path objects
"""

import threading
from pathlib import Path

import whisper

from config import WHISPER_MODEL

_model = None
_lock = threading.Lock()

# Whisper language code mapping
_LANG_MAP = {
    "english": "en",
    "hindi": "hi",
    "hinglish": "hi",   # transcribe as Hindi, translation handled upstream
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "japanese": "ja",
    "portuguese": "pt",
}


def load_model() -> whisper.Whisper:
    global _model
    with _lock:
        if _model is None:
            print(f"Loading Whisper model '{WHISPER_MODEL}'…")
            _model = whisper.load_model(WHISPER_MODEL)
            print("Whisper model loaded.")
    return _model


def transcribe_chunk(chunk_path: str | Path, language: str = "english") -> str:
    """Transcribe a single audio chunk. Returns raw text."""
    model = load_model()
    lang_code = _LANG_MAP.get(language.lower(), language.lower())

    # For Hinglish: transcribe in Hindi then let summarizer handle code-switching
    result = model.transcribe(str(chunk_path), task="transcribe", language=lang_code)
    return result["text"]


def transcribe_all(
    chunks: list,
    language: str = "english",
    progress_callback=None,
) -> str:
    """
    Transcribe all chunks and return full concatenated transcript.
    progress_callback(current, total) is called after each chunk if provided.
    """
    full_transcript = ""
    total = len(chunks)

    for i, chunk in enumerate(chunks, start=1):
        print(f"Transcribing chunk {i}/{total}…")
        text = transcribe_chunk(chunk, language=language)
        full_transcript += text + " "
        if progress_callback:
            progress_callback(i, total)

    print("Transcription complete.")
    return full_transcript.strip()
