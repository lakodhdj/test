from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.account.models import User
from app.account.schemas import (
    PasswordChangeRequest,
    PasswordResetEmailRequest,
    PasswordResetRequest,
    UserCreate,
    UserLogin,
)
from app.account.utils import (
    create_email_verification_token,
    create_password_reset_token,
    get_user_by_email,
    hash_password,
    verify_email_token_and_get_user_id,
    verify_password,
)
from app.account.email import send_verification_email


async def create_user(session: AsyncSession, user: UserCreate):
    if not user.accepted_terms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользовательское соглашение должно быть принято",
        )

    stmt = select(User).where(User.email == user.email)
    result = await session.scalars(stmt)
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_verified=False,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def authenticate_user(session: AsyncSession, user_login: UserLogin):
    stmt = select(User).where(User.email == user_login.email)
    result = await session.scalars(stmt)
    user = result.first()

    if not user or not verify_password(user_login.password, user.hashed_password):
        return None
    return user


async def email_verification_send(user: User):
    token = create_email_verification_token(user.id)

    # Отправляем реальное письмо
    await send_verification_email(user.email, token)

    return {"msg": "Verification email sent successfully. Please check your inbox."}


async def verify_email_token(session: AsyncSession, token: str):
    user_id = verify_email_token_and_get_user_id(token, "verify_email")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    stmt = select(User).where(User.id == user_id)
    result = await session.scalars(stmt)
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.is_verified = True  # исправлено
    session.add(user)
    await session.commit()
    return {"msg": "Email verified successfully"}


async def change_password(
    session: AsyncSession, user: User, data: PasswordChangeRequest
):
    # Проверяем старый пароль
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect"
        )

    # Меняем пароль
    user.hashed_password = hash_password(data.new_password)
    session.add(user)
    await session.commit()

    return {"msg": "Password changed successfully"}


async def password_reset_email_send(
    session: AsyncSession, data: PasswordResetEmailRequest
):
    user = await get_user_by_email(session, data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    token = create_password_reset_token(user.id)
    link = f"http://localhost:8000/account/password-reset?token={token}"
    print(f"Reset your password: {link}")
    return {"msg": "Password reset email sent"}


async def verify_password_reset_token(
    session: AsyncSession, data: PasswordResetRequest
):
    user_id = verify_email_token_and_get_user_id(data.token, "password_reset")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    stmt = select(User).where(User.id == user_id)
    result = await session.scalars(stmt)
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.hashed_password = hash_password(data.new_password)
    session.add(user)
    await session.commit()
    return {"msg": "Password reset successfully"}
