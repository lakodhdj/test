from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from app.db.config import SessionDep
from app.account.schemas import (
    PasswordChangeRequest,
    PasswordResetEmailRequest,
    PasswordResetRequest,
    UserCreate,
    UserLogin,
    UserOut,
)
from app.account.services import (
    change_password,
    create_user,
    email_verification_send,
    verify_email_token,
    authenticate_user,
    password_reset_email_send,
    verify_password_reset_token,
)
from app.account.models import User
from app.account.deps import get_current_user, require_admin
from app.account.utils import (
    create_tokens,
    verify_refresh_token,
    revoke_refresh_token,
)
from sqlalchemy import func
from app.order.models import Order
from app.product.models import Product

router = APIRouter(tags=["Account"])


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, session: SessionDep):
    return await create_user(session=session, user=user)


@router.post("/login")
async def login(user_login: UserLogin, session: SessionDep):
    user = await authenticate_user(session, user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    tokens = await create_tokens(user)  # ← передаём только user

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user


@router.post("/refresh")
async def refresh_token(request: Request, session: SessionDep):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )

    # Новая версия с Redis
    user_id = await verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Получаем пользователя из БД
    stmt = select(User).where(User.id == user_id)
    result = await session.scalars(stmt)
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    tokens = await create_tokens(user)

    response = JSONResponse(content={"message": "Token refreshed successfully"})
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=False,  # для разработки можно False
        samesite="lax",
        max_age=60 * 60 * 24 * 1,  # 1 день
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.post("/send-verification-email")
async def send_verification_email(user: User = Depends(get_current_user)):
    return await email_verification_send(user)


@router.get("/verify-email")
async def verify_email(session: SessionDep, token: str):
    return await verify_email_token(session, token)


@router.post("/change-password")
async def password_change(
    session: SessionDep,
    data: PasswordChangeRequest,
    user: User = Depends(get_current_user),
):
    await change_password(session, user, data)
    return {"msg": "Password changed successfully"}


@router.post("/send-password-reset-email")
async def send_password_reset_email(
    session: SessionDep, data: PasswordResetEmailRequest
):
    return await password_reset_email_send(session, data)


@router.post("/verify-password-reset-token")
async def verify_password_reset_token_route(
    session: SessionDep, data: PasswordResetRequest
):
    return await verify_password_reset_token(session, data)


@router.get("/admin")
async def admin(user: User = Depends(require_admin)):
    return {"msg": f"Welcome admin {user.email}!"}


@router.get("/admin/stats")
async def admin_stats(session: SessionDep, user: User = Depends(require_admin)):
    orders_count = await session.scalar(select(func.count(Order.id))) or 0
    products_count = await session.scalar(select(func.count(Product.id))) or 0
    return {
        "orders_count": orders_count,
        "products_count": products_count,
    }


@router.post("/logout")
async def logout(
    request: Request, session: SessionDep, user: User = Depends(get_current_user)
):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        await revoke_refresh_token(refresh_token)  # ← теперь асинхронно с Redis

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


