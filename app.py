import streamlit as st
import tempfile, os
from config import Config
from chat import get_reply, get_rag_reply, load_history, save_history
from rag import load_pdf, build_vectorstore, load_vectorstore, vectorstore_exists
from agents import run_agent
import json  

cfg = Config()
cfg.validate()
st.set_page_config(page_title="AI Chat + RAG", page_icon="📄")

# ── Session state ────────────────────────────────────────
for key, val in {"messages": [], "total_tokens": 0, "vectorstore": None}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:

    st.header("Settings")
    cfg.SYSTEM_PROMPT = st.text_area("System Prompt", value=cfg.SYSTEM_PROMPT)
    cfg.DOCUMENT_PROMPT = st.text_area("Document Prompt", value=cfg.DOCUMENT_PROMPT)

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

    if st.session_state.vectorstore:
        if st.button("Clear Vector Database", use_container_width=True):
            st.session_state.vectorstore = None
            st.info("Vector database cleared from memory.")

    # Load an existing vector database
    if vectorstore_exists() and st.session_state.vectorstore is None:
        st.session_state.vectorstore = load_vectorstore(cfg.OPENAI_API_KEY)
        st.info("Database loaded from cache")

    # Add mode selection:
    mode = st.radio("Mode", ["💬 Chat", "📄 Documents", "🤖 Agent"])
    show_context = st.checkbox("Show Sources", value=False)
    st.divider()
    st.metric("Tokens", st.session_state.total_tokens)
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.rerun()

# ── Header ───────────────────────────────────────────────
mode_label = "📄 Document Mode" if mode == "📄 Documents" else "🤖 Agent Mode" if mode == "🤖 Agent" else "💬 Regular Chat"
st.title(f"AI Chat — {mode_label}")

# ── Chat History ─────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input ────────────────────────────────────────────────
if prompt := st.chat_input("Ask the agent a task..." if mode == "🤖 Agent" else "Write a message..." if mode == "💬 Chat" else "Ask a question about the document..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    if mode == "🤖 Agent":
        with st.chat_message("assistant"):
            with st.spinner("Agent is working..."):
                answer, log = run_agent(prompt)

            st.markdown(answer)

            # Display agent steps
            with st.expander(f"Agent Steps ({len(log)})"):
                for i, s in enumerate(log, 1):
                    st.write(f"**Step {i}:** {s['step']}")
                    if "args" in s:
                        st.code(json.dumps(s["args"], ensure_ascii=False))
                    if "result" in s:
                        st.caption(s["result"])

    elif mode == "📄 Documents" and st.session_state.vectorstore:
        with st.chat_message("assistant"):
            with st.spinner("Searching in documents..."):
                reply, history, tokens, context = get_rag_reply(
                    prompt, st.session_state.messages,
                    cfg, st.session_state.vectorstore
                )
        st.markdown(reply)
        if show_context and context:
            with st.expander("Sources"):
                st.text(context)

    else:  # Default to Chat mode
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply, history, tokens = get_reply(
                    prompt, st.session_state.messages, cfg
                )
        st.markdown(reply)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": reply if mode != "🤖 Agent" else answer})
    st.session_state.total_tokens += tokens if mode != "🤖 Agent" else 0