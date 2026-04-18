import uuid
import asyncio

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.agent import create_agent
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.models.tenant import Tenant
from app.core.exceptions import QuotaExceededException
from app.schemas.chat import ChatRequest, ChatResponse, SourceReference
from app.services.rag_service import RAGService


class ChatService:
    """Service for handling AI chat interactions."""

    def __init__(self, db: AsyncSession, rag_service: RAGService | None):
        self.db = db
        self.rag_service = rag_service

    async def process_message(self, request: ChatRequest, user: User) -> ChatResponse:
        """Process a chat message and return AI response."""
        # Check quota
        tenant = await self._get_tenant(user.tenant_id)
        if user.queries_this_month >= tenant.max_queries_per_month:
            raise QuotaExceededException()

        # Get or create conversation
        conversation = await self._get_or_create_conversation(
            request.conversation_id, user, request.mode
        )

        # Get context from RAG
        context = ""
        if self.rag_service:
            context = await self.rag_service.get_context(request.message, request.mode)
        else:
            context = "No RAG context available."

        # Get conversation history BEFORE saving current message
        chat_history = await self._get_chat_history(conversation.id)

        # Save user message immediately so concurrent requests see it
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )
        self.db.add(user_message)
        await self.db.flush()

        # Run agent with retry for transient errors (503, 429)
        agent = create_agent(request.mode)
        result = None
        ai_response = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = agent.invoke({
                    "input": request.message,
                    "context": context,
                    "chat_history": chat_history,
                })
                ai_response = result.get("output", "I'm sorry, I couldn't process your request.")
                # Gemini returns list of content blocks; extract text
                if isinstance(ai_response, list):
                    parts = []
                    for part in ai_response:
                        if isinstance(part, dict) and "text" in part:
                            parts.append(part["text"])
                        elif isinstance(part, str):
                            parts.append(part)
                    ai_response = "".join(parts)
                break  # Success
            except Exception as e:
                error_msg = str(e)
                is_retryable = "503" in error_msg or "UNAVAILABLE" in error_msg or "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg
                if is_retryable and attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt * 5)  # 5s, 10s, 20s
                    continue
                if "insufficient_quota" in error_msg or "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    ai_response = "⚠️ The AI service is temporarily rate-limited. Please wait a moment and try again. The calculators (tax, GST, TDS) still work without the AI service."
                elif "503" in error_msg or "UNAVAILABLE" in error_msg:
                    ai_response = "⚠️ The AI model is experiencing high demand. Please try again in a few seconds."
                else:
                    ai_response = f"Sorry, an error occurred while processing your request: {error_msg}"
                result = {"intermediate_steps": []}


        sources = self._extract_sources(result.get("intermediate_steps", []))

        # Detect tool usage
        tool_used = None
        for step in result.get("intermediate_steps", []):
            if hasattr(step[0], "tool"):
                tool_used = step[0].tool
                break

        # Save assistant response
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            sources={"references": [s.model_dump() for s in sources]} if sources else None,
            tool_used=tool_used,
        )

        self.db.add(assistant_message)

        # Update query count
        user.queries_this_month += 1

        # Update conversation title if it's the first message
        if conversation.title == "New Conversation":
            conversation.title = request.message[:100]

        await self.db.commit()

        return ChatResponse(
            message=ai_response,
            conversation_id=conversation.id,
            sources=sources,
            tool_used=tool_used,
        )

    async def _get_tenant(self, tenant_id: str) -> Tenant:
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one()

    async def _get_or_create_conversation(
        self, conversation_id: str | None, user: User, mode: str
    ) -> Conversation:
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user.id,
                )
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation

        conversation = Conversation(
            tenant_id=user.tenant_id,
            user_id=user.id,
            mode=mode,
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def _get_chat_history(self, conversation_id: str) -> list:
        from langchain_core.messages import HumanMessage, AIMessage

        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(20)
        )
        messages = result.scalars().all()

        history = []
        for msg in reversed(messages):
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))

        return history

    def _extract_sources(self, intermediate_steps: list) -> list[SourceReference]:
        sources = []
        # Sources come from RAG context, not directly from agent steps
        # In a more advanced setup, we'd track which documents were retrieved
        return sources

    async def get_conversations(self, user: User, limit: int = 50):
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user.id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_conversation(self, conversation_id: str, user: User):
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id,
            )
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def delete_conversation(self, conversation_id: str, user: User) -> bool:
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.commit()
        return True
