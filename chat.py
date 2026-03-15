import json
import datetime

def add_message(history, role, content):
    message = {"role": role, 
               "content": content,
               "timestamp": datetime.datetime.now().isoformat()
               }
    history.append(message)
    return history

def save_history(history, filename):
    with open(filename, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(history)} messages to {filename}")

def load_history(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []   # no file, start with empty line
    
def print_history(history):
    for i, msg in enumerate(history,1):
        prefix = "You" if msg["role"] == "user" else "AI"
        time_str = msg['timestamp'][11:16]
        print(f"{i}. [{time_str}] {prefix}: {msg['content']}")
    
# Use: 
chat = load_history("chat.json")
add_message(chat, "user", "Hi!, how are you?")
add_message(chat, "assistant", "Great!, how can I help you?")
add_message(chat, "user", "I need to check something!")


print_history(chat)

save_history(chat, "chat.json")
