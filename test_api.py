import requests

BASE = "http://localhost:8001"

# Health check
r = requests.get(f"{BASE}/health")
print("Health:", r.json())

# First message
r = requests.post(f"{BASE}/chat", json={
    "message": "My name is Tony",
    "session_id": "tony_session"
})
print('Answer 1:', r.json()["reply"])

# Second message, check history
r = requests.post(f"{BASE}/chat", json={
    "message": "What is my name?",
    "session_id": "tony_session"
})
print('Answer 2:', r.json()["reply"])

# Agent
r = requests.post(f"{BASE}/agent", json = {
    "task": "Find last news about Ottawa"
})
print("Agent:", r.json()["answer"][:200])

session_id = "tony_session"
history_url = f"{BASE}/chat/{session_id}/history"

print(f"\n--- Checking history for session: {session_id} ---")
r_history = requests.get(history_url)

if r_history.status_code == 200:
    history_data = r_history.json()
    messages = history_data.get("history", [])
    print(f"Successfully retrieved {len(messages)} messages.")
    
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        print(f"{i+1}. [{role.upper()}]: {content}")
else:
    print(f"Error fetching history: {r_history.status_code}")
    print(r_history.text)
