from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: str | None = None
    mode: str = Field(default="general", pattern="^(accounting|legal|general)$")


class SourceReference(BaseModel):
    document: str
    chunk: str
    relevance_score: float


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    sources: list[SourceReference] = []
    tool_used: str | None = None
    tokens_used: int = 0
    disclaimer: str = "AI-generated response. Verify with a qualified professional before acting on this information."


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: dict | None
    tool_used: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: str
    title: str
    mode: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}


class ConversationListItem(BaseModel):
    id: str
    title: str
    mode: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}
