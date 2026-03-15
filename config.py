import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #API:
    OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL           = os.getenv("MODEL", "gpt-4o-mini")

    #Limits:
    MAX_TOKENS = 500
    MAX_HISTORY = 20
    MAX_RETRIES = 3
    TIMEOUT = 30

    # Files:
    HISTORY_FILE = "chat_history.json"

    # Prompts:
    SYSTEM_PROMPT = "Ты профессиональный шутник и в каждом ответе шутишь"

    def validate(self):
        if not self.OPEN_AI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.") 
        return True
    
