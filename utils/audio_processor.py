"""
utils/audio_processor.py — Audio acquisition, conversion, and chunking.

Fixes vs original:
- ffmpeg_location no longer hardcoded to Windows path; uses config.FFMPEG_LOCATION
- Chunk temp files are tracked and can be cleaned up by caller
- WAV conversion uses 1-channel 16 kHz (Whisper requirement)
- process_input returns (chunks, cleanup_fn) so callers can delete temp files
"""

import os
import uuid
from pathlib import Path
from typing import Callable

import yt_dlp
from pydub import AudioSegment

from config import DOWNLOAD_DIR, AUDIO_CHUNK_MINUTES, AUDIO_SAMPLE_RATE, FFMPEG_LOCATION


def download_youtube_audio(url: str) -> Path:
    """Download best audio from a YouTube URL and return path to WAV file."""
    unique_id = uuid.uuid4().hex[:8]
    output_template = str(DOWNLOAD_DIR / f"yt_{unique_id}.%(ext)s")

    ydl_opts: dict = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    if FFMPEG_LOCATION:
        ydl_opts["ffmpeg_location"] = FFMPEG_LOCATION

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        original = Path(ydl.prepare_filename(info))

    wav_path = original.with_suffix(".wav")
    if not wav_path.exists():
        raise FileNotFoundError(f"Download succeeded but WAV not found at {wav_path}")
    return wav_path


def convert_to_wav(input_path: str | Path) -> Path:
    """Convert any audio/video file to mono 16 kHz WAV."""
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = DOWNLOAD_DIR / f"{input_path.stem}_converted_{uuid.uuid4().hex[:6]}.wav"
    audio = AudioSegment.from_file(str(input_path))
    audio = audio.set_channels(1).set_frame_rate(AUDIO_SAMPLE_RATE)
    audio.export(str(output_path), format="wav")
    return output_path


def chunk_audio(wav_path: Path, chunk_minutes: int = AUDIO_CHUNK_MINUTES) -> list[Path]:
    """Split a WAV file into N-minute chunks. Returns list of chunk paths."""
    audio = AudioSegment.from_wav(str(wav_path))
    chunk_ms = chunk_minutes * 60 * 1000
    chunks: list[Path] = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = wav_path.parent / f"{wav_path.stem}_chunk_{i}.wav"
        chunk.export(str(chunk_path), format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> tuple[list[Path], Callable[[], None]]:
    """
    Process a YouTube URL or local file path.
    Returns: (chunks, cleanup_fn)
    """
    temp_files: list[Path] = []

    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL — downloading audio…")
        wav_path = download_youtube_audio(source)
        temp_files.append(wav_path)
    else:
        print("Detected local file — converting to WAV…")
        wav_path = convert_to_wav(source)
        temp_files.append(wav_path)

    print("Chunking audio…")
    chunks = chunk_audio(wav_path)
    temp_files.extend(chunks)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    def cleanup():
        for f in temp_files:
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass

    return chunks, cleanup
