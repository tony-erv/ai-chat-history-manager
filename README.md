# AI Chat History Manager 🤖

This is a practice project that implements a persistent memory system for AI agents.

### Features:
- **JSON Persistence:** Saves chat history in a structured JSON format (industry standard for OpenAI and Anthropic APIs).
- **Timestamps:** Automatically adds ISO-formatted timestamps to every message for tracking.
- **Session Continuity:** Loads existing history on startup, allowing for continuous multi-session dialogues.
- **Formatted Output:** Displays the conversation in the console with clear numbering and role identification.

### Technologies:
- **Python 3.x**
- **JSON & Datetime** (standard libraries)

### How to Run:
1. Clone the repository to your local machine.
2. Ensure you have Python installed.
3. Run the script using:
   ```bash
   python main.py