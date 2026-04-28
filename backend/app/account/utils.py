from datetime import timedelta, datetime, timezone
from decouple import config
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any
import uuid
import redis.asyncio as redis
import bcrypt

from app.account.models import User

JWT_SECRET_KEY = config("JWT_SECRET_KEY", default="your_very_strong_secret_key_here_change_in_prod")
JWT_ALGORITHM = config("JWT_ALGORITHM", default="HS256")
JWT_ACCESS_TOKEN_TIME_MIN = config("JWT_ACCESS_TOKEN_TIME_MIN", cast=int, default=30)
JWT_REFRESH_TOKEN_TIME_DAY = config("JWT_REFRESH_TOKEN_TIME_DAY", cast=int, default=7)
EMAIL_VERIFICATION_TOKEN_TIME_HOUR = config(
    "EMAIL_VERIFICATION_TOKEN_TIME_HOUR", cast=int, default=1
)
EMAIL_PASSWORD_RESET_TOKEN_TIME_HOUR = config(
    "EMAIL_PASSWORD_RESET_TOKEN_TIME_HOUR", cast=int, default=2
)

REDIS_ENABLED = config("REDIS_ENABLED", cast=bool, default=False)
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"


class InMemoryRedis:
    def __init__(self):
        self._storage: dict[str, Any] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._storage[key] = value

    async def get(self, key: str) -> str | None:
        return self._storage.get(key)

    async def delete(self, key: str) -> None:
        self._storage.pop(key, None)


redis_client = (
    redis.from_url(REDIS_URL, decode_responses=True)
    if REDIS_ENABLED
    else InMemoryRedis()
)


def hash_password(password: str) -> str:
    """Хэширует пароль с помощью bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_TIME_MIN)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def create_tokens(user: User):
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token_str = str(uuid.uuid4())

    await redis_client.set(
        f"refresh_token:{refresh_token_str}",
        str(user.id),
        ex=JWT_REFRESH_TOKEN_TIME_DAY * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
    }


def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def verify_refresh_token(token: str):
    user_id = await redis_client.get(f"refresh_token:{token}")
    if not user_id:
        return None
    return int(user_id)


async def revoke_refresh_token(token: str):
    await redis_client.delete(f"refresh_token:{token}")


# ====================== Email & Password Reset ======================
def create_email_verification_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(
        hours=EMAIL_VERIFICATION_TOKEN_TIME_HOUR
    )
    to_encode = {"sub": str(user_id), "type": "verify_email", "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_password_reset_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(
        hours=EMAIL_PASSWORD_RESET_TOKEN_TIME_HOUR
    )
    to_encode = {"sub": str(user_id), "type": "password_reset", "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_email_token_and_get_user_id(token: str, token_type: str):
    payload = decode_token(token)
    if not payload or payload.get("type") != token_type:
        return None
    return int(payload.get("sub"))


async def get_user_by_email(session: AsyncSession, email: str):
    """Недостающая функция, из-за которой была ошибка"""
    stmt = select(User).where(User.email == email)
    result = await session.scalars(stmt)
    return result.first()
