"""
ui/chat_view.py — RAG chat panel.
"""

import streamlit as st


def render_chat(rag_chain):
    st.markdown(
        '<div class="section-header">'
        '<div class="section-icon">💬</div>'
        '<h3>Chat with your content</h3>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption("Ask anything — the AI has read the full transcript.")

    # ── Chat history ──────────────────────────────────────────────────────────
    chat_container = st.container(height=420)
    with chat_container:
        history = st.session_state.get("chat_history", [])
        if not history:
            st.markdown(
                """
                <div class="chat-empty">
                    <div class="chat-empty-icon">💬</div>
                    <div class="chat-empty-text">
                        Ask a question about the meeting.<br>
                        <span style="opacity:0.6; font-size:0.75rem;">
                            e.g. "What were the main decisions?" or "Who owns the Q3 deliverable?"
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for msg in history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # ── Input ─────────────────────────────────────────────────────────────────
    question = st.chat_input("Ask a question about the meeting…", key="chat_input")

    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        from core.rag_engine import ask_question
                        answer = ask_question(rag_chain, question)
                    except Exception as e:
                        answer = f"⚠️ Error: {e}"
                st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # ── Clear ─────────────────────────────────────────────────────────────────
    if st.session_state.get("chat_history"):
        if st.button("🗑  Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
