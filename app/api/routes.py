import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from langchain_core.messages import HumanMessage, AIMessage

from app.api.schemas import ChatRequest, ChatResponse, SessionInfo
from app.agent.graph import get_graph
from app.agent.memory import (
    get_history, save_message, clear_session,
    get_all_sessions, format_history_for_llm
)
import os
import shutil

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint — sends message to AI agent."""
    
    # Create or reuse session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Save user message
    save_message(session_id, "user", request.message)
    
    # Build message history for agent
    history = format_history_for_llm(session_id)
    messages = [HumanMessage(content=msg["content"]) 
                if msg["role"] == "user" 
                else AIMessage(content=msg["content"])
                for msg in history]
    
    try:
        graph = get_graph()
        result = graph.invoke({"messages": messages})
        
        # Extract final response
        last_message = result["messages"][-1]
        response_text = last_message.content
        
        # Detect tools used
        tools_used = []
        for msg in result["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tools_used.extend([tc["name"] for tc in msg.tool_calls])
        
        # Save assistant response
        save_message(session_id, "assistant", response_text)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            tools_used=list(set(tools_used)),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[SessionInfo])
def list_sessions():
    """List all active sessions."""
    sessions = get_all_sessions()
    result = []
    for sid in sessions:
        history = get_history(sid)
        result.append(SessionInfo(session_id=sid, message_count=len(history)))
    return result


@router.get("/history/{session_id}")
def get_session_history(session_id: str):
    """Get full conversation history for a session."""
    history = get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "history": history}


@router.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Clear a session's conversation history."""
    clear_session(session_id)
    return {"message": f"Session {session_id} cleared"}


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF for the agent to read."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, os.path.basename(file.filename))
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return {"message": f"PDF uploaded: {file.filename}", "path": file_path}
