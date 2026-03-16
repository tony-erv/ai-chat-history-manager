import streamlit as st
import tempfile, os
from config import Config
from chat import get_reply, get_rag_reply, load_history, save_history
from rag import load_pdf, build_vectorstore, load_vectorstore, vectorstore_exists

cfg = Config()
cfg.validate()
st.set_page_config(page_title="AI Chat + RAG", page_icon="📄")

# ── Session state ────────────────────────────────────────
for key, val in {"messages": [], "total_tokens": 0, "vectorstore": None}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.header("Documents")

    uploaded = st.file_uploader("Upload a PDF", type="pdf")
    if uploaded and st.button("Process Document", use_container_width=True):
        with st.spinner("Creating vector database..."):
            # Save the uploaded file to a temporary directory
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                f.write(uploaded.getvalue())
                tmp_path = f.name
            chunks = load_pdf(tmp_path)
            st.session_state.vectorstore = build_vectorstore(chunks, cfg.OPENAI_API_KEY)
            os.unlink(tmp_path)  # Remove the temporary file
        st.success(f"Done! {len(chunks)} chunks added to the database.")

    # Load an existing vector database
    if vectorstore_exists() and st.session_state.vectorstore is None:
        st.session_state.vectorstore = load_vectorstore(cfg.OPENAI_API_KEY)
        st.info("Database loaded from cache")

    rag_mode = st.toggle(
        "Document Mode",
        value=st.session_state.vectorstore is not None,
        disabled=st.session_state.vectorstore is None
    )
    show_context = st.checkbox("Show Sources", value=False)
    st.divider()
    st.metric("Tokens", st.session_state.total_tokens)
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.rerun()

# ── Header ───────────────────────────────────────────────
mode_label = "📄 Document Mode" if rag_mode else "💬 Regular Chat"
st.title(f"AI Chat — {mode_label}")

# ── Chat History ─────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input ────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about the document..." if rag_mode else "Write a message..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching in documents..." if rag_mode else "Thinking..."):
            if rag_mode and st.session_state.vectorstore:
                reply, history, tokens, context = get_rag_reply(
                    prompt, st.session_state.messages,
                    cfg, st.session_state.vectorstore
                )
            else:
                reply, history, tokens = get_reply(
                    prompt, st.session_state.messages, cfg
                )
                context = None

        st.markdown(reply)
        if show_context and context:
            with st.expander("Sources"):
                st.text(context)

    st.session_state.messages = history
    st.session_state.total_tokens += tokens