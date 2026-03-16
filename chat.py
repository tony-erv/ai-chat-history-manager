import json
import os
import time
import logging
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError
from config import Config
from rag import search

logger = logging.getLogger(__name__)
cfg = Config()
cfg.validate()

client = OpenAI(api_key=cfg.OPEN_AI_API_KEY)

def load_history(history_file):
    try:
        with open(history_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_history(history, history_file):
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def show_history():
    history = load_history()
    if not history:
        print("No chat history found.")
        return

    print("Chat History:")
    for entry in history:
        role = entry["role"]
        content = entry["content"]
        print(f"{role.capitalize()}: {content}\n")

def clear_history():
    if os.path.exists(cfg.HISTORY_FILE):
        os.remove(cfg.HISTORY_FILE)
        print("Chat history cleared.")
    else:
        print("No chat history to clear.")

def safe_chat(messages, retries=cfg.MAX_RETRIES):
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to send message. Attempt {attempt + 1}/{retries}")
            response = client.chat.completions.create(
                model=cfg.MODEL,
                messages=messages,
                max_tokens=cfg.MAX_TOKENS,
                timeout=cfg.TIMEOUT
            )
            logger.info("Response received successfully. Tokens used: %d", response.usage.total_tokens)
            reply = response.choices[0].message.content
            return reply, response.usage.total_tokens  # Возвращаем ответ и количество токенов

        except RateLimitError:
            logger.warning("RateLimitError on attempt %d.", attempt + 1)
            time.sleep(2 ** attempt)

        except AuthenticationError:
            logger.error("Authentication failed. Check your API key.")
            raise

        except APIConnectionError:
            logger.warning("Connection error. Retrying %d/%d...", attempt + 1, retries)
            time.sleep(5)

    return "Sorry, I'm having trouble responding right now. Please try again later.", 0

def chat(user_input, history):
    history.append({"role": "user", "content": user_input})
    filtered_history = history[-cfg.MAX_HISTORY:]

    messages = [{"role": "system", "content": cfg.SYSTEM_PROMPT}] + filtered_history
    ai_reply, tokens = safe_chat(messages)
    history.append({"role": "assistant", "content": ai_reply})
    return ai_reply, history

def get_reply(user_input, history, cfg):
    messages = (
        [{"role": "system", "content": cfg.SYSTEM_PROMPT}]
        + history[-cfg.MAX_HISTORY:]
        + [{"role": "user", "content": user_input}]
    )
    # Передаем cfg.MAX_RETRIES вместо cfg
    reply, tokens = safe_chat(messages, cfg.MAX_RETRIES)

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})
    return reply, history, tokens

def get_rag_reply(user_input, history, cfg, vectorstore):
    context = search(vectorstore, user_input, k=4)
    rag_system_prompt = f"""{cfg.SYSTEM_PROMPT}

Answer ONLY based on the following context from the document. 
If the answer is not in the context, say you don't know.
Don't make up answers. Always use the context.
Context: {context}"""
    
    messages = (
        [{"role": "system", "content": rag_system_prompt}]
        + history[-cfg.MAX_HISTORY:]
        + [{"role": "user", "content": user_input}]
    )
    reply, tokens = safe_chat(messages, cfg.MAX_RETRIES)

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})
    return reply, history, tokens, context