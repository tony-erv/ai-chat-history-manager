import streamlit as st
from config import Config
from chat import get_reply, load_history, save_history
import logging

logger = logging.getLogger(__name__)

cfg = Config()
cfg.validate()

st.set_page_config(
    page_title="AI Chat by Tony Ervalson", 
    page_icon="🤖", 
    layout="centered"
)

if "messages" not in st.session_state:
    st.session_state.messages = load_history(cfg.HISTORY_FILE)
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

with st.sidebar:
    st.header("Настройки")
    cfg.SYSTEM_PROMPT = st.text_area(
        "System prompt", 
        value=cfg.SYSTEM_PROMPT, 
        height=100
    )
    cfg.MODEL = st.selectbox("Model:", ["gpt-4o-mini", "gpt-4o"])
    cfg.MAX_TOKENS = st.slider("Max Tokens", 100, 2000, cfg.MAX_TOKENS)
    st.divider()
    st.metric("Tokens", st.session_state.total_tokens)
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        save_history([], cfg.HISTORY_FILE)
        st.rerun()

st.title("AI Chat with History")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Напиши сообщение..."):
    if prompt.strip():  # Проверка на пустую строку
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                reply, history, tokens = get_reply(
                    prompt,
                    st.session_state.messages,
                    cfg
                )
            st.markdown(reply)

        st.session_state.messages = history
        st.session_state.total_tokens += tokens
        save_history(history, cfg.HISTORY_FILE)