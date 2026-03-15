import os
import time
import json
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError
from config import Config
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chat.log"),
        logging.StreamHandler()
    ])

logger = logging.getLogger(__name__)
#logger.info("Starting chat application...")
#logger.warning("History close to limit, consider clearing old messages.")
#logger.error("API error: %s", "RateLimitError") 

cfg = Config()
cfg.validate()
client = OpenAI(api_key=cfg.OPEN_AI_API_KEY)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

HISTORY_FILE = Config.HISTORY_FILE
SYSTEM_PROMPT = Config.SYSTEM_PROMPT
MODEL = Config.MODEL
MAX_TOKENS = Config.MAX_TOKENS

def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return [] 
    
def save_history(history):
    with open(HISTORY_FILE, "w") as f:
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
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        print("Chat history cleared.")
    else:
        print("No chat history to clear.")

def validate_message(text):
    return bool(text) and len(text) < 2000

def safe_chat(messages, retries=3):
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to send message. Attempt {attempt + 1}/{retries}")
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS,
                timeout=Config.TIMEOUT
            )
            logger.info("Response received successfully. Tokens used: %d", response.usage.total_tokens)
            return response.choices[0].message.content
        
        except RateLimitError:
            logger.warning("RateLimitError on attempt %d.", attempt + 1)

        except AuthenticationError:
            print(f"Authentication failed. Check your API key.")
            raise

        except APIConnectionError:
            print(f"Connection error. Retrying {attempt + 1}/{retries}...")
            time.sleep(5)

    return "Sorry, I'm having trouble responding right now. Please try again later."    

def chat(user_input, history):
    history.append({"role": "user", "content": user_input})

    filtered_history = list(filter(lambda msg: validate_message(msg["content"]), history))[-Config.MAX_HISTORY:]
    messages=[
            {
                "role":"system",
                "content": SYSTEM_PROMPT
                } 
        ] + filtered_history
    
    ai_reply = safe_chat(messages)
    history.append({"role": "assistant", "content": ai_reply})
    return ai_reply, history

def main():
    history = load_history()
    print(f"Chat started. History: {len(history)} messages. Type 'exit' to quit., 'history' to show history, 'clear' to clear history.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['exit', 'quit']:
            save_history(history)
            print
            break

        if user_input.lower() == 'history':
            show_history()
            continue

        if user_input.lower() == 'clear':
            clear_history()
            history = []
            continue
        
        if not user_input:
            continue    
        
        reply, history = chat(user_input, history)
        print(f"AI: {reply}\n")
    
if __name__ == "__main__":
    main()