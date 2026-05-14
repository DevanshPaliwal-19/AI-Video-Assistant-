
import sys
import os

# Ensure project root (parent of frontend/) is on path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(_project_root, ".env"))

import streamlit as st
from ui.layout import render_header, render_sidebar
from ui.pipeline_view import render_pipeline_runner
from ui.chat_view import render_chat
from ui.results_view import render_results

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ─────────────────────────────────────────────────────────────────
_css_path = os.path.join(os.path.dirname(__file__), "ui", "styles.css")
with open(_css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────────
_defaults = {
    "pipeline_result": None,
    "rag_chain": None,
    "chat_history": [],
    "processing": False,
    "error": None,
    "pipeline_step": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Render ─────────────────────────────────────────────────────────────────────
render_header()
source, language = render_sidebar()

# Two-column layout: pipeline + results | chat
left, right = st.columns([3, 2], gap="large")

with left:
    render_pipeline_runner(source, language)
    if st.session_state.pipeline_result:
        render_results(st.session_state.pipeline_result)

with right:
    if st.session_state.rag_chain:
        render_chat(st.session_state.rag_chain)
    else:
        st.markdown(
            """
            <div class="glass-card" style="margin-top:2.5rem;">
                <div class="chat-empty">
                    <div class="chat-empty-icon">🔒</div>
                    <div class="chat-empty-text">
                        <strong style="color: var(--text-secondary);">Chat locked</strong><br>
                        <span style="font-size:0.78rem; opacity:0.7;">
                            Run the pipeline first to unlock<br>Q&amp;A over your content.
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
