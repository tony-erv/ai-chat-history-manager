# Chatbot with OpenAI API 🤖

This is a Python chatbot that interacts with OpenAI's GPT model. It supports:
- Message history with a limit.
- Validation of user input.
- Logging for debugging and monitoring.

## Features
- **Configurable**: All settings are in `config.py`.
- **History Management**: Save, load, and clear chat history.
- **Error Handling**: Handles API errors gracefully.

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
    python main.py
