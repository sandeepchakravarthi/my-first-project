from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    tools_used: List[str] = []
    timestamp: str


class SessionInfo(BaseModel):
    session_id: str
    message_count: int


class HealthResponse(BaseModel):
    status: str
    agent: str
