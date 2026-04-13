from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.calculator import router as calculator_router
from app.api.admin import router as admin_router

__all__ = ["auth_router", "chat_router", "documents_router", "calculator_router", "admin_router"]
