# app/order/routers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.db.config import SessionDep
from app.account.deps import get_current_user
from app.account.models import User
from app.order.models import Order, OrderItem, OrderStatus
from app.order.schemas import OrderCreate
from app.cart.models import CartItem

router = APIRouter(tags=["Orders"])


@router.post("/")
async def create_order(
    order_data: OrderCreate,
    session: SessionDep,
    user: User = Depends(get_current_user),
):
    # Получаем товары из корзины пользователя (CartItem)
    stmt = (
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.user_id == user.id)
    )
    result = await session.execute(stmt)
    cart_items = result.scalars().all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Подсчитываем общую сумму
    total_amount = sum(item.quantity * item.product.price for item in cart_items)

    # Создаём заказ
    new_order = Order(
        user_id=user.id,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        status=OrderStatus.PENDING,
    )
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)

    # Добавляем товары в заказ
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price_at_purchase=cart_item.product.price,
        )
        session.add(order_item)

    # Очищаем корзину после создания заказа
    await session.execute(delete(CartItem).where(CartItem.user_id == user.id))
    await session.commit()

    return {
        "message": "Order created successfully",
        "order_id": new_order.id,
        "total_amount": total_amount,
    }


@router.get("/")
async def get_user_orders(session: SessionDep, user: User = Depends(get_current_user)):
    stmt = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
    )
    result = await session.execute(stmt)
    orders = result.scalars().all()

    return {
        "orders": [
            {
                "id": order.id,
                "total_amount": order.total_amount,
                "status": order.status.value,
                "shipping_address": order.shipping_address,
                "created_at": order.created_at.isoformat(),
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price_at_purchase": item.price_at_purchase,
                        "product_title": item.product.title if item.product else None,
                    }
                    for item in order.items
                ],
            }
            for order in orders
        ]
    }


@router.get("/{order_id}")
async def get_order_detail(
    order_id: int, session: SessionDep, user: User = Depends(get_current_user)
):
    stmt = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.id == order_id, Order.user_id == user.id)
    )
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "id": order.id,
        "total_amount": order.total_amount,
        "status": order.status.value,
        "shipping_address": order.shipping_address,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_at_purchase": item.price_at_purchase,
                "product_title": item.product.title if item.product else None,
            }
            for item in order.items
        ],
    }
