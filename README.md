# Chatbot with OpenAI API 🤖

This is a Python chatbot that interacts with OpenAI's GPT model. It supports:
- Message history with a limit.
- Validation of user input.
- Logging for debugging and monitoring.

---

## Features
- **Configurable**: All settings are in `config.py`.
- **History Management**: Save, load, and clear chat history.
- **Error Handling**: Handles API errors gracefully.
- **Input Validation**: Ensures user messages are non-empty and under 2000 characters.

---

## 🛠 Tech Stack
- **Language:** Python 3.x
- **API:** OpenAI (GPT-4o-mini)
- **Data:** JSON for local persistence
- **Environment:** `python-dotenv`

---

## 📦 Quick Start

1. **Clone & Enter:**
   ```bash
   git clone https://github.com/tony-erv/ai-chat-history-manager.git
   cd ai-chat-history-manager
   ```

2. **Setup Environment:**
   - Create a `.env` file in the project root.
   - Add your OpenAI API key:
     ```env
     OPENAI_API_KEY=your_actual_key_here
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Chatbot:**
   ```bash
   python main.py
   ```

---

## Usage

### Commands:
- `exit` or `quit`: End the chat session and save history.
- `history`: Display the current chat history.
- `clear`: Clear the chat history.

### Example Interaction:
```
Chat started. History: 0 messages. Type 'exit' to quit, 'history' to show history, 'clear' to clear history.

You: Hello!
AI: Hi there! How can I assist you today?

You: history
Chat History:
User: Hello!
AI: Hi there! How can I assist you today?

You: exit
Chat ended. History saved.
```

---

## Configuration

All settings are managed in `config.py`:
- **API Settings**:
  - `OPEN_AI_API_KEY`: Your OpenAI API key.
  - `MODEL`: The GPT model to use (default: `gpt-4o-mini`).
- **Limits**:
  - `MAX_TOKENS`: Maximum tokens per response.
  - `MAX_HISTORY`: Maximum number of messages to retain in history.
  - `MAX_RETRIES`: Maximum retries for API calls.
  - `TIMEOUT`: Timeout for API requests.
- **Files**:
  - `HISTORY_FILE`: File to save chat history.
- **Prompts**:
  - `SYSTEM_PROMPT`: Initial system message for the chatbot.

---

## Logging

Logs are saved to `chat.log` and include:
- Application events (e.g., "Chat started").
- Warnings (e.g., "History close to limit").
- Errors (e.g., "API error: RateLimitError").

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

**Tony Ervalson**  
Feel free to reach out with questions or suggestions!