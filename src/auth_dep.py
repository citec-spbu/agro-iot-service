import uuid
from dataclasses import dataclass

import httpx
from fastapi import Header, HTTPException, status

from src.config import settings


@dataclass(frozen=True)
class TokenPayload:
    sub: uuid.UUID
    role: str
    email: str
    org: uuid.UUID


async def require_user(authorization: str | None = Header(None)) -> TokenPayload:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{settings.AUTH_SERVICE_URL.rstrip('/')}/api/auth/introspect",
            headers={"Authorization": authorization},
        )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    data = response.json()
    try:
        return TokenPayload(
            sub=uuid.UUID(str(data["sub"])),
            role=str(data["role"]),
            email=str(data["email"]),
            org=uuid.UUID(str(data["org"])),
        )
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload",
        ) from exc
