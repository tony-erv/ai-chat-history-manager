import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

HISTORY_FILE = "chat_history.json"
SYSTEM_PROMPT = "You are cybesecurity hacker, and you answer use hacker words."

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


def chat(user_input, history):
    history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role":"system",
                "content": SYSTEM_PROMPT
                },
        ] + history,
        max_tokens=300
    )

    ai_reply = response.choices[0].message.content
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