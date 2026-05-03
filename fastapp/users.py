import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (AuthenticationBackend, BearerTransport, JWTStrategy)

SECRET = "jwt-secret-key"
class UserManager(UUIDIDMixin, BaseUserManager[models.UP, models.ID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    async def on_after_register(self, user: models.UP, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
    async def on_after_forgot_password(self, user: models.UP, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")
    async def on_after_request_verify(self, user: models.UP, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
    
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)
auth_backend = AuthenticationBackend(name="jwt", transport=bearer_transport, get_strategy=get_j