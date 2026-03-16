import os


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    # API:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("MODEL", "gpt-4o-mini")

    # Limits:
    MAX_TOKENS = 500
    MAX_HISTORY = 20
    MAX_RETRIES = 3
    TIMEOUT = 30

    # Files:
    HISTORY_FILE = "chat_history.json"

    # Prompts:
    SYSTEM_PROMPT = "You are a helpful assistant."
    DOCUMENT_PROMPT = "Answer ONLY based on the following context from the document.  If the answer is not in the context, say you don't know. Don't make up answers. Always use the context."

    def validate(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
        return True