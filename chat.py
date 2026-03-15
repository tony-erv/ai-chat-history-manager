import json

def add_message(history, role, content):
    message = {"role": role, "content": content}
    history.append(message)
    return history

def save_history(history, filename):
    with open(filename, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"Сохранено {len(history)} сообщений")

def load_history(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []   # файла нет — начинаем с пустой истории
    
def print_history():
    with open("chat.json", "r") as f:
        loaded = json.load(f)
        print(loaded)

# Используем
chat = load_history("chat.json")
add_message(chat, "user", "Привет, как дела?")
add_message(chat, "assistant", "Отлично! Готов учиться?")
add_message(chat, "user", "Да, поехали!")
save_history(chat, "chat.json")

print_history()

