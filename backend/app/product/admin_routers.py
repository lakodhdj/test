from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    Form,
    File,
)
from app.account.models import User
from app.db.config import SessionDep
from app.account.deps import require_admin
from app.product.models import Product, Category, Gender, Size
from app.product.schemas import ProductCreate, ProductOut
from app.product.services import create_product, get_all_products
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def admin_create_product(
    session: SessionDep,
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    gender: Gender = Form(...),
    size: Size = Form(...),
    category_ids: Annotated[list[int] | None, Form()] = [],
    image_url: UploadFile | None = File(None),
    admin_user: User = Depends(require_admin),
):
    """Создать новый товар (только для админов)"""
    data = ProductCreate(
        title=title,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        gender=gender,
        size=size,
        category_ids=category_ids or [],
    )
    return await create_product(session, data, image_url)


@admin_router.put("/products/{product_id}", response_model=ProductOut)
async def admin_update_product(
    session: SessionDep,
    product_id: int,
    title: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    stock_quantity: int = Form(None),
    gender: Gender = Form(None),
    size: Size = Form(None),
    category_ids: Annotated[list[int] | None, Form()] = None,
    image_url: UploadFile | None = File(None),
    admin_user: User = Depends(require_admin),
):
    """Обновить товар (только для админов)"""
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Обновляем поля если переданы
    if title:
        product.title = title
    if description:
        product.description = description
    if price is not None:
        product.price = price
    if stock_quantity is not None:
        product.stock_quantity = stock_quantity
    if gender:
        product.gender = gender
    if size:
        product.size = size

    if category_ids is not None:
        stmt = select(Category).where(Category.id.in_(category_ids))
        result = await session.execute(stmt)
        product.categories = result.scalars().all()

    session.add(product)
    await session.commit()
    await session.refresh(product, ["categories"])
    return product


@admin_router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_product(
    session: SessionDep,
    product_id: int,
    admin_user: User = Depends(require_admin),
):
    """Удалить товар (только для админов)"""
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await session.delete(product)
    await session.commit()
    return None


@admin_router.get("/products/all", response_model=list[ProductOut])
async def admin_get_all_products(
    session: SessionDep,
    admin_user: User = Depends(require_admin),
):
    """Получить все товары (только для админов)"""
    stmt = select(Product)
    result = await session.execute(stmt)
    return result.scalars().all()


@admin_router.post("/products/{product_id}/stock", response_model=ProductOut)
async def admin_update_stock(
    session: SessionDep,
    product_id: int,
    stock_quantity: int = Form(...),
    admin_user: User = Depends(require_admin),
):
    """Обновить количество товара на складе (только для админов)"""
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if stock_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock quantity cannot be negative",
        )

    product.stock_quantity = stock_quantity
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product
