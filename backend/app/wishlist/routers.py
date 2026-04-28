# app/wishlist/routers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from app.db.config import SessionDep
from app.account.deps import get_current_user
from app.account.models import User
from app.product.models import Product
from app.wishlist.wishlist import wishlist_table

router = APIRouter(tags=["Wishlist"])


@router.post("/{product_id}")
async def add_to_wishlist(
    product_id: int, session: SessionDep, user: User = Depends(get_current_user)
):
    # Проверяем, существует ли товар
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Проверяем, есть ли уже в избранном
    stmt = select(wishlist_table).where(
        wishlist_table.c.user_id == user.id, wishlist_table.c.product_id == product_id
    )
    result = await session.execute(stmt)
    if result.first():
        raise HTTPException(status_code=400, detail="Product already in wishlist")

    # Добавляем в избранное
    stmt = wishlist_table.insert().values(user_id=user.id, product_id=product_id)
    await session.execute(stmt)
    await session.commit()

    return {"msg": "Product added to wishlist"}


@router.delete("/{product_id}")
async def remove_from_wishlist(
    product_id: int, session: SessionDep, user: User = Depends(get_current_user)
):
    stmt = wishlist_table.delete().where(
        wishlist_table.c.user_id == user.id, wishlist_table.c.product_id == product_id
    )
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not in wishlist")

    return {"msg": "Product removed from wishlist"}


@router.get("/")
async def get_wishlist(session: SessionDep, user: User = Depends(get_current_user)):
    stmt = (
        select(Product)
        .join(wishlist_table, Product.id == wishlist_table.c.product_id)
        .where(wishlist_table.c.user_id == user.id)
    )
    result = await session.execute(stmt)
    products = result.scalars().all()

    return {"items": products}
