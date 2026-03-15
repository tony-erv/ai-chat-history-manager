# Custom AI CLI Chatbot 🤖

A flexible Python-based command-line interface for interacting with OpenAI models. This project features a modular design, allowing you to easily swap "AI personas" and manage conversation memory.

### 🚀 Key Features
- **Configurable Persona:** Easily change the `SYSTEM_PROMPT` to switch between different AI roles (Hacker, Assistant, Tutor, etc.).
- **Persistent History:** Automatically saves and loads chat logs using `chat_history.json`.
- **Session Management:**
  - `history`: Display all messages from the current and past sessions.
  - `clear`: Reset the conversation and delete the local history file.
  - `exit/quit`: Gracefully exit and ensure the current session is saved.
- **Environment Security:** Uses `.env` to keep your API keys safe and out of version control.

### 🛠 Tech Stack
- **Language:** Python 3.x
- **API:** OpenAI (GPT-4o-mini)
- **Data:** JSON for local persistence
- **Environment:** `python-dotenv`

### 📦 Quick Start

1. **Clone & Enter:**
   ```bash
   git clone [https://github.com/tony-erv/ai-chat-history-manager.git](https://github.com/tony-erv/ai-chat-history-manager.git)
   cd ai-chat-history-manager

2. **Setup Environment:**
    Create a .env file.
    Add your key: OPENAI_API_KEY=your_actual_key_here

3. **Install & Run:**
    ```bash
    pip install openai python-dotenv
    python chat.py
