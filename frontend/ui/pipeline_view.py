"""
ui/pipeline_view.py — Pipeline runner with step-by-step progress display.
"""

import sys
import os
import streamlit as st
from ui.layout import validate_source

# Pipeline steps for UI display
PIPELINE_STEPS = [
    ("🎵", "Acquiring audio"),
    ("🎤", "Transcribing audio"),
    ("🏷️", "Generating title"),
    ("📝", "Summarizing content"),
    ("✅", "Extracting action items"),
    ("🔑", "Extracting key decisions"),
    ("❓", "Extracting open questions"),
    ("🗂️", "Building RAG index"),
]


def _render_step_list(current_step: int | None = None):
    """Render animated pipeline step list."""
    items_html = ""
    for i, (icon, label) in enumerate(PIPELINE_STEPS):
        if current_step is None:
            cls = ""
            dot_cls = ""
            dot_inner = ""
        elif i < current_step:
            cls = "done"
            dot_cls = "done"
            dot_inner = "✓"
        elif i == current_step:
            cls = "active"
            dot_cls = "active"
            dot_inner = "…"
        else:
            cls = ""
            dot_cls = ""
            dot_inner = ""

        items_html += f"""
        <div class="pipeline-step">
            <div class="step-dot {dot_cls}">{dot_inner}</div>
            <div class="step-label {cls}">{icon} {label}</div>
        </div>
        """

    st.markdown(
        f'<div class="pipeline-steps">{items_html}</div>',
        unsafe_allow_html=True,
    )


def render_pipeline_runner(source: str, language: str):
    st.markdown(
        '<div class="section-header">'
        '<div class="section-icon">🚀</div>'
        '<h3>Run Pipeline</h3>'
        '</div>',
        unsafe_allow_html=True,
    )

    run = st.button(
        "▶  Run Pipeline",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.get("processing", False),
    )

    if run:
        error = validate_source(source)
        if error:
            st.error(f"⚠️ {error}")
            return

        # Reset state
        st.session_state.processing = True
        st.session_state.error = None
        st.session_state.pipeline_result = None
        st.session_state.rag_chain = None
        st.session_state.chat_history = []
        st.session_state.pipeline_step = 0

        step_placeholder = st.empty()

        def update_step(msg: str, pct: float):
            """Map progress message to step index."""
            step_map = {
                "Acquiring": 0,
                "Transcribing": 1,
                "Generating": 2,
                "Summarizing": 3,
                "action": 4,
                "decisions": 5,
                "questions": 6,
                "RAG": 7,
            }
            idx = next(
                (i for key, i in step_map.items() if key.lower() in msg.lower()),
                st.session_state.get("pipeline_step", 0),
            )
            st.session_state.pipeline_step = idx
            with step_placeholder.container():
                _render_step_list(current_step=idx)

        with step_placeholder.container():
            _render_step_list(current_step=0)

        try:
            # Ensure project root on path
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            from main import run_pipeline

            result = run_pipeline(
                source=source.strip(),
                language=language,
                progress_callback=update_step,
            )

            st.session_state.pipeline_result = result
            st.session_state.rag_chain = result.get("rag_chain")
            st.session_state.pipeline_step = len(PIPELINE_STEPS)  # all done

            with step_placeholder.container():
                _render_step_list(current_step=len(PIPELINE_STEPS))

            st.success("✅ Pipeline complete — results below.")

        except ImportError as e:
            st.session_state.error = f"Import error — check that all dependencies are installed.\n\n`{e}`"
        except EnvironmentError as e:
            st.session_state.error = str(e)
        except Exception as e:
            st.session_state.error = str(e)
        finally:
            st.session_state.processing = False

    # Show prior step state if not running
    elif st.session_state.get("pipeline_result"):
        _render_step_list(current_step=len(PIPELINE_STEPS))
    elif not st.session_state.get("processing"):
        st.caption("Enter a source in the sidebar and click Run Pipeline.")

    if st.session_state.get("error"):
        st.error(f"❌ {st.session_state.error}")
        with st.expander("Troubleshooting"):
            st.markdown(
                """
- Confirm the YouTube URL is public and accessible.
- For local files, verify the path is correct and the file is readable.
- Check your `.env` contains `MISTRAL_API_KEY`.
- Run `pip install -r requirements.txt` to ensure all dependencies are installed.
- Set `FFMPEG_LOCATION` in `.env` if ffmpeg is not on your system PATH.
                """
            )
