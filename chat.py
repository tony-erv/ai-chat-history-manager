import json
import os
import time
import logging
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError
from config import Config

logger = logging.getLogger(__name__)
cfg = Config()
cfg.validate()

client = OpenAI(api_key=cfg.OPEN_AI_API_KEY)

def load_history():
    try:
        with open(cfg.HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_history(history):
    with open(cfg.HISTORY_FILE, "w") as f:
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
            return response.choices[0].message.content

        except RateLimitError:
            logger.warning("RateLimitError on attempt %d.", attempt + 1)
            time.sleep(2 ** attempt)

        except AuthenticationError:
            logger.error("Authentication failed. Check your API key.")
            raise

        except APIConnectionError:
            logger.warning("Connection error. Retrying %d/%d...", attempt + 1, retries)
            time.sleep(5)

    return "Sorry, I'm having trouble responding right now. Please try again later."

def chat(user_input, history):
    history.append({"role": "user", "content": user_input})
    filtered_history = history[-cfg.MAX_HISTORY:]

    messages = [{"role": "system", "content": cfg.SYSTEM_PROMPT}] + filtered_history
    ai_reply = safe_chat(messages)
    history.append({"role": "assistant", "content": ai_reply})
    return ai_reply, history