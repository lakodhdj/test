# app/cart/routers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.db.config import SessionDep
from app.account.deps import get_current_user
from app.account.models import User
from app.product.models import Product
from app.cart.models import CartItem

router = APIRouter(tags=["Cart"])


@router.post("/{product_id}")
async def add_to_cart(
    session: SessionDep,
    product_id: int,
    quantity: int = 1,
    user: User = Depends(get_current_user),
):
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    # Проверяем существование товара
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Проверяем, есть ли уже в корзине
    stmt = select(CartItem).where(
        CartItem.user_id == user.id, CartItem.product_id == product_id
    )
    existing = await session.scalar(stmt)

    if existing:
        existing.quantity += quantity
    else:
        cart_item = CartItem(user_id=user.id, product_id=product_id, quantity=quantity)
        session.add(cart_item)

    await session.commit()
    return {"message": "Product added to cart"}


@router.delete("/{product_id}")
async def remove_from_cart(
    product_id: int, session: SessionDep, user: User = Depends(get_current_user)
):
    stmt = delete(CartItem).where(
        CartItem.user_id == user.id, CartItem.product_id == product_id
    )
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not in cart")

    return {"message": "Product removed from cart"}


@router.put("/{product_id}")
async def update_cart_item(
    session: SessionDep,
    product_id: int,
    quantity: int = 1,
    user: User = Depends(get_current_user),
):
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stmt = select(CartItem).where(
        CartItem.user_id == user.id, CartItem.product_id == product_id
    )
    existing = await session.scalar(stmt)

    if not existing:
        raise HTTPException(status_code=404, detail="Product not in cart")

    existing.quantity = quantity
    await session.commit()

    return {"message": "Cart item updated"}


@router.get("/")
async def get_cart(session: SessionDep, user: User = Depends(get_current_user)):
    stmt = (
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.user_id == user.id)
    )
    result = await session.execute(stmt)
    cart_items = result.scalars().all()

    total_amount = sum(item.quantity * item.product.price for item in cart_items)

    return {
        "items": [
            {
                "product": item.product,
                "quantity": item.quantity,
                "subtotal": item.quantity * item.product.price,
            }
            for item in cart_items
        ],
        "total_amount": total_amount,
    }


@router.get("/")
async def get_cart(session: SessionDep, user: User = Depends(get_current_user)):
    stmt = (
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.user_id == user.id)
    )
    result = await session.execute(stmt)
    cart_items = result.scalars().all()

    total_amount = sum(item.quantity * item.product.price for item in cart_items)

    return {
        "items": [
            {
                "product": item.product,
                "quantity": item.quantity,
                "subtotal": item.quantity * item.product.price,
            }
            for item in cart_items
        ],
        "total_amount": total_amount,
    }


@router.delete("/")
async def clear_cart(session: SessionDep, user: User = Depends(get_current_user)):
    stmt = delete(CartItem).where(CartItem.user_id == user.id)
    await session.execute(stmt)
    await session.commit()
    return {"message": "Cart cleared"}
