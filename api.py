import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from config import Config
from chat import get_reply
from agents import run_agent

load_dotenv()
cfg = Config()
cfg.validate()

app = FastAPI(title="DSN AI Chat API", version="1.0")

# Allow CORS for all origins (for testing purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (for demonstration; replace with DB in production)
sessions: dict[str, list] = {}

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message:    str
    session_id: str = "default"

class ChatResponse(BaseModel):
    reply:       str
    tokens_used: int
    session_id:  str
    history_len: int

class AgentRequest(BaseModel):
    task:      str
    max_steps: int = 5

class AgentResponse(BaseModel):
    answer: str
    steps:  list

# ── Endpoints ────────────────────────────────────────────
@app.get("/health")
def health():
    """
    Check API status and loaded configuration.
    """
    from chat import sessions_db
    return {
        "status": "ok", 
        "model": cfg.MODEL, 
        "active_sessions": len(sessions_db)
    }

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    Main chat endpoint. Handles history persistence per session_id.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    # Import dictionary from chat module to ensure global state consistency
    from chat import sessions_db, get_reply

    # Retrieve existing history or initialize a new list for the session
    history = sessions_db.get(req.session_id, [])

    # Process message through the logic in chat.py
    # Returns: (str) reply, (list) updated_history, (int) tokens
    reply, updated_history, tokens = get_reply(req.message, history, cfg)

    # Save the updated history back to the global dictionary
    sessions_db[req.session_id] = updated_history

    return ChatResponse(
        reply=reply,
        tokens_used=tokens,
        session_id=req.session_id,
        history_len=len(updated_history)
    )

@app.get("/chat/{session_id}/history")
def get_session_history(session_id: str):
    """
    Retrieve all messages associated with a specific session_id.
    """
    from chat import sessions_db 
    
    history = sessions_db.get(session_id)
    
    if history is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    
    return {
        "session_id": session_id,
        "history": history,
        "count": len(history)
    }

@app.post("/agent", response_model=AgentResponse)
def agent_endpoint(req: AgentRequest):
    """
    Triggers an autonomous agent to perform complex tasks (Web Search, Tools).
    """
    if not req.task.strip():
        raise HTTPException(status_code=400, detail="Empty task")

    # Assuming run_agent is imported and accepts max_steps parameter
    # answer: str, steps: list
    answer, steps = run_agent(req.task, max_steps=req.max_steps)
    
    return AgentResponse(
        answer=answer, 
        steps=steps
    )

@app.delete("/chat/{session_id}")
def clear_session(session_id: str):
    """
    Wipe history for a specific session. Use with caution.
    """
    from chat import sessions_db
    if session_id in sessions_db:
        sessions_db.pop(session_id)
        return {"status": "deleted", "session_id": session_id}
    
    raise HTTPException(status_code=404, detail="Session not found")

# Run the app with: uvicorn api:app --host
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)