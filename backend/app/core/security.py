import uuid
import logging

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()

_jwks_client = None


def get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        jwks_url = settings.clerk_jwks_url or f"{settings.clerk_jwt_issuer}/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True)
    return _jwks_client


async def verify_clerk_token(token: str) -> dict:
    """Verify JWT token using Clerk's JWKS public keys."""
    try:
        client = get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.clerk_jwt_issuer or None,
            options={
                "verify_aud": False,  # Clerk session tokens don't have aud
                "verify_iss": bool(settings.clerk_jwt_issuer),
            },
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and verify the current user from the auth token."""
    token = credentials.credentials
    clerk_data = await verify_clerk_token(token)
    clerk_user_id = clerk_data.get("sub")

    if not clerk_user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Auto-register user on first Clerk-authenticated request
        logger.info(f"Auto-registering new user: {clerk_user_id}")
        email = clerk_data.get("email", clerk_data.get("email_addresses", [{}])[0].get("email_address", "") if isinstance(clerk_data.get("email_addresses"), list) else "")
        full_name = clerk_data.get("name", clerk_data.get("first_name", ""))
        if not email:
            email = f"{clerk_user_id}@clerk.user"
        if not full_name:
            full_name = email.split("@")[0]

        tenant_name = f"{full_name}'s Workspace"
        slug = tenant_name.lower().replace(" ", "-").replace("'", "")
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        tenant = Tenant(
            name=tenant_name,
            slug=slug,
            plan="free",
            max_users=1,
            max_documents=5,
            max_queries_per_month=50,
        )
        db.add(tenant)
        await db.flush()

        user = User(
            tenant_id=tenant.id,
            clerk_user_id=clerk_user_id,
            email=email,
            full_name=full_name,
            role="admin",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
