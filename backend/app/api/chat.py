from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationListItem,
)
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService

router = APIRouter()


def _get_rag_service(request: Request) -> RAGService | None:
    return request.app.state.rag_service


@router.post("/", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(_get_rag_service),
):
    """Send a message to the AI assistant and get a response."""
    service = ChatService(db, rag_service)
    return await service.process_message(chat_request, user)


@router.get("/conversations", response_model=list[ConversationListItem])
async def list_conversations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(_get_rag_service),
):
    """List all conversations for the current user."""
    service = ChatService(db, rag_service)
    conversations = await service.get_conversations(user)
    return [
        ConversationListItem(
            id=c.id,
            title=c.title,
            mode=c.mode,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(_get_rag_service),
):
    """Get a specific conversation with all messages."""
    service = ChatService(db, rag_service)
    conversation = await service.get_conversation(conversation_id, user)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends(_get_rag_service),
):
    """Delete a conversation."""
    service = ChatService(db, rag_service)
    deleted = await service.delete_conversation(conversation_id, user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}
