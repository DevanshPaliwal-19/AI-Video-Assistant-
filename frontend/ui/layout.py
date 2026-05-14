"""
ui/layout.py — Sidebar and page header.
"""

import re
import streamlit as st
from config import SUPPORTED_LANGUAGES


def render_header():
    st.markdown(
        """
        <div class="app-header">
            <div class="header-badge">🎙️</div>
            <div>
                <h1 class="header-title">
                    AI Video <span class="accent">Assistant</span>
                </h1>
                <p class="header-sub">Transcribe · Summarize · Chat with your content</p>
                <div class="header-pills">
                    <span class="pill active">Whisper STT</span>
                    <span class="pill active">Mistral LLM</span>
                    <span class="pill active">RAG Chat</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<hr style="margin: 0.75rem 0 1rem; opacity: 0.4;">', unsafe_allow_html=True)


def render_sidebar() -> tuple[str, str]:
    with st.sidebar:
        # Logo
        st.markdown(
            """
            <div class="sidebar-logo">
                <div class="sidebar-logo-icon">🎙️</div>
                <span class="sidebar-logo-text">AI Video Assistant</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Source config ─────────────────────────────────────────────────────
        st.markdown('<p class="sidebar-section-label">Source</p>', unsafe_allow_html=True)

        input_type = st.radio(
            "Input type",
            ["YouTube URL", "Local file path"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if input_type == "YouTube URL":
            source = st.text_input(
                "YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Paste any public YouTube video or meeting recording URL.",
                label_visibility="collapsed",
            )
        else:
            source = st.text_input(
                "File path",
                placeholder="/path/to/meeting.mp4  or  recording.wav",
                help="Absolute or relative path to a local audio/video file.",
                label_visibility="collapsed",
            )

        # ── Language ──────────────────────────────────────────────────────────
        st.markdown('<p class="sidebar-section-label">Transcription Language</p>', unsafe_allow_html=True)
        language = st.selectbox(
            "Language",
            SUPPORTED_LANGUAGES,
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # ── Status ────────────────────────────────────────────────────────────
        st.markdown('<p class="sidebar-section-label">Status</p>', unsafe_allow_html=True)

        if st.session_state.get("pipeline_result"):
            st.markdown(
                '<div class="status-indicator ready">'
                '<div class="status-dot"></div>Pipeline complete</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.get("processing"):
            st.markdown(
                '<div class="status-indicator idle">'
                '<div class="status-dot pulse"></div>Processing…</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-indicator idle">'
                '<div class="status-dot"></div>Idle — enter source above</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ── Reset ─────────────────────────────────────────────────────────────
        if st.button("↺  Reset session", use_container_width=True):
            for k in ["pipeline_result", "rag_chain", "chat_history", "error", "processing", "pipeline_step"]:
                st.session_state[k] = None if k in ["pipeline_result", "rag_chain", "error", "pipeline_step"] else ([] if k == "chat_history" else False)
            st.rerun()

        st.markdown("")
        st.markdown(
            '<span class="version-tag">v2.0.0-prod</span>',
            unsafe_allow_html=True,
        )

    return source or "", language


def validate_source(source: str) -> str | None:
    """Returns an error string or None if valid."""
    if not source.strip():
        return "Source cannot be empty."
    youtube_pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
    if source.startswith("http") and not re.match(youtube_pattern, source):
        return "URL doesn't look like a valid YouTube link."
    return None
