"""
ui/results_view.py — Renders pipeline output with stats and structured tabs.
"""

import streamlit as st


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _estimate_duration(word_count: int) -> str:
    """Rough estimate: average speech is ~130 words/min."""
    minutes = word_count / 130
    if minutes < 1:
        return "<1 min"
    return f"~{minutes:.0f} min"


def render_results(result: dict):
    transcript = result.get("transcript", "")
    wc = _word_count(transcript)

    st.markdown('<hr style="opacity:0.3; margin: 1rem 0;">', unsafe_allow_html=True)

    # ── Title ──────────────────────────────────────────────────────────────────
    title = result.get("title", "Untitled")
    st.markdown(f"### 📄 {title}")

    # ── Stats bar ─────────────────────────────────────────────────────────────
    summary_wc = _word_count(result.get("summary", ""))
    action_count = result.get("action_items", "").count("\n1.") + (
        1 if result.get("action_items", "").strip().startswith("1.") else 0
    )

    st.markdown(
        f"""
        <div class="stat-row">
            <div class="stat-chip">
                <span class="stat-chip-value">{wc:,}</span>
                <span class="stat-chip-label">Words</span>
            </div>
            <div class="stat-chip">
                <span class="stat-chip-value">{_estimate_duration(wc)}</span>
                <span class="stat-chip-label">Duration</span>
            </div>
            <div class="stat-chip">
                <span class="stat-chip-value">{summary_wc}</span>
                <span class="stat-chip-label">Summary words</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab_summary, tab_actions, tab_decisions, tab_questions, tab_transcript = st.tabs(
        ["📝 Summary", "✅ Actions", "🔑 Decisions", "❓ Questions", "📜 Transcript"]
    )

    with tab_summary:
        summary = result.get("summary", "")
        if summary:
            st.markdown(summary)
        else:
            st.info("No summary generated.")

    with tab_actions:
        items = result.get("action_items", "")
        if items and "no action items" not in items.lower():
            st.markdown(items)
        else:
            st.info("No action items found in this content.")

    with tab_decisions:
        decisions = result.get("key_decisions", "")
        if decisions and "no key decisions" not in decisions.lower():
            st.markdown(decisions)
        else:
            st.info("No key decisions found in this content.")

    with tab_questions:
        questions = result.get("open_questions", "")
        if questions and "no open questions" not in questions.lower():
            st.markdown(questions)
        else:
            st.info("No open questions found in this content.")

    with tab_transcript:
        if transcript:
            st.markdown(
                f'<div class="transcript-wrap">{transcript}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No transcript available.")

        st.download_button(
            "⬇  Download transcript (.txt)",
            data=transcript,
            file_name="transcript.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ── Download full report ───────────────────────────────────────────────────
    st.markdown('<div class="download-strip">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇  Full report (.md)",
            data=_build_report(result),
            file_name="meeting_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "⬇  Summary only (.txt)",
            data=result.get("summary", ""),
            file_name="summary.txt",
            mime="text/plain",
            use_container_width=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _build_report(result: dict) -> str:
    title = result.get("title", "Meeting Report")
    sections = [
        f"# {title}",
        "",
        "## Summary",
        result.get("summary", ""),
        "",
        "## Action Items",
        result.get("action_items", ""),
        "",
        "## Key Decisions",
        result.get("key_decisions", ""),
        "",
        "## Open Questions",
        result.get("open_questions", ""),
        "",
        "## Full Transcript",
        result.get("transcript", ""),
    ]
    return "\n".join(s for s in sections)
