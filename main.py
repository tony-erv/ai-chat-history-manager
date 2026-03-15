from chat import chat, load_history, save_history, show_history, clear_history
from config import Config
from utils import validate_message
import logging

logger = logging.getLogger(__name__)

def main():
    history = load_history()
    print(f"Chat started. History: {len(history)} messages. Type 'exit' to quit, 'history' to show history, 'clear' to clear history.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['exit', 'quit']:
            save_history(history)
            print("Chat ended. History saved.")
            break

        if user_input.lower() == 'history':
            show_history()
            continue

        if user_input.lower() == 'clear':
            clear_history()
            history = []
            continue

        if not validate_message(user_input):
            print("Invalid input. Please enter a non-empty message under 2000 characters.")
            continue

        reply, history = chat(user_input, history)
        print(f"AI: {reply}\n")

if __name__ == "__main__":
    main()