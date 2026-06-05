import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timezone

# In-memory store (replace with Redis in production)
_sessions: Dict[str, List[Dict]] = {}


def get_history(session_id: str) -> List[Dict]:
    """Get conversation history for a session."""
    return _sessions.get(session_id, [])


def save_message(session_id: str, role: str, content: str):
    """Save a message to session history."""
    if session_id not in _sessions:
        _sessions[session_id] = []
    
    _sessions[session_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Keep last 20 messages
    if len(_sessions[session_id]) > 20:
        _sessions[session_id] = _sessions[session_id][-20:]


def clear_session(session_id: str):
    """Clear conversation history for a session."""
    if session_id in _sessions:
        del _sessions[session_id]


def get_all_sessions() -> List[str]:
    """Get all active session IDs."""
    return list(_sessions.keys())


def format_history_for_llm(session_id: str) -> List[Dict]:
    """Format history as LangChain messages."""
    history = get_history(session_id)
    messages = []
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    return messages
