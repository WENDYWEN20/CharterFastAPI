import os
from datetime import datetime, timedelta

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Keep this auth module aligned with the FastAPI Users JWT secret.
from fastapp.users import SECRET as FASTAPI_USERS_SECRET

ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET", FASTAPI_USERS_SECRET)

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    subject: str,
    role: str = "user",
    expires_delta: timedelta | None = None,
) -> str:
    expires_at = datetime.utcnow() + (expires_delta or timedelta(hours=1))
    payload = {"sub": subject, "role": role, "exp": expires_at}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc


def get_request_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_token: str | None = Cookie(default=None),
) -> str:
    # Accept token from Authorization Bearer first, then fallback to HttpOnly cookie.
    if credentials and credentials.credentials:
        return credentials.credentials
    if auth_token:
        return auth_token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication token",
    )


def get_current_token_payload(token: str = Depends(get_request_token)) -> dict:
    return decode_access_token(token)


def require_admin(payload: dict = Depends(get_current_token_payload)) -> dict:
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return payload