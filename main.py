"""
main.py — Core pipeline orchestrator.

Usage (CLI):
    python main.py

The pipeline runs sequentially:
1. Audio acquisition + chunking
2. Transcription (Whisper)
3. Title generation
4. Summarization (map-reduce)
5. Extraction: action items, decisions, open questions
6. RAG chain construction
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Fix encoding for Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from config import validate_env
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain


def run_pipeline(
    source: str,
    language: str = "english",
    progress_callback=None,
) -> dict:
    """
    Run the full AI pipeline on a YouTube URL or local file.

    Args:
        source: YouTube URL or local file path.
        language: Language hint for Whisper transcription.
        progress_callback: Optional callable(step: str, pct: float) for UI updates.

    Returns:
        dict with keys: title, transcript, summary, action_items,
                        key_decisions, open_questions, rag_chain
    """
    errors = validate_env()
    if errors:
        raise EnvironmentError(f"Configuration errors: {'; '.join(errors)}")

    def _step(msg: str, pct: float):
        print(f"[{pct:.0%}] {msg}")
        if progress_callback:
            progress_callback(msg, pct)

    _step("Acquiring audio…", 0.0)
    chunks, cleanup = process_input(source)

    _step("Transcribing audio…", 0.15)
    transcript = transcribe_all(chunks, language=language)
    print(f"Transcript preview: {transcript[:200]}…")

    # Clean up temp audio files after transcription
    cleanup()

    _step("Generating title…", 0.40)
    title = generate_title(transcript)

    _step("Summarizing content…", 0.50)
    summary = summarize(transcript)

    _step("Extracting action items…", 0.65)
    action_items = extract_action_items(transcript)

    _step("Extracting key decisions…", 0.75)
    decisions = extract_key_decisions(transcript)

    _step("Extracting open questions…", 0.85)
    questions = extract_questions(transcript)

    _step("Building RAG index…", 0.92)
    rag_chain = build_rag_chain(transcript)

    _step("Pipeline complete.", 1.0)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


if __name__ == "__main__":
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish/hindi/...): ").strip() or "english"
    result = run_pipeline(source, language)

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"TITLE: {result['title']}")
    print(f"\nSUMMARY:\n{result['summary']}")
    print(f"\nACTION ITEMS:\n{result['action_items']}")
    print(f"\nKEY DECISIONS:\n{result['key_decisions']}")
    print(f"\nOPEN QUESTIONS:\n{result['open_questions']}")
    print(sep)

    print("\nCHAT with your meeting (type 'exit' to quit)\n")
    rag_chain = result["rag_chain"]
    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break
        if not question:
            continue
        answer = result["rag_chain"].invoke(question)
        print(f"\nASSISTANT: {answer}\n")
