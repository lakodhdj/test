from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.product.models import Product, Category
from app.product.schemas import (
    CategoryCreate,
    CategoryOut,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    PaginatedProductOut,
)
from app.product.utils import generate_slug, save_upload_file
from sqlalchemy.orm import selectinload


######################## Category ########################
async def create_category(session: AsyncSession, category: CategoryCreate):
    category = Category(name=category.name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def get_all_categories(session: AsyncSession):
    stmt = select(Category)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_category(session: AsyncSession, category_id: int):
    category = await session.get(Category, category_id)
    if not category:
        return False
    await session.delete(category)
    await session.commit()
    return True


######################## Category ########################
async def create_product(
    session: AsyncSession, data: ProductCreate, image_file: UploadFile | None = None
):
    if data.stock_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock quantity cannot be negative",
        )

    image_path = data.image_url
    if image_file:
        image_path = await save_upload_file(image_file, "images") or image_path

    # Получаем категории
    categories = []
    if data.category_ids:
        stmt = select(Category).where(Category.id.in_(data.category_ids))
        result = await session.execute(stmt)
        categories = result.scalars().all()

    # Подготавливаем данные
    product_dict = data.model_dump(exclude={"category_ids"})

    if not product_dict.get("title"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required"
        )

    product_dict["slug"] = generate_slug(product_dict["title"])

    # Создаём продукт с новыми полями gender и size
    new_product = Product(**product_dict, image_url=image_path, categories=categories)

    session.add(new_product)
    await session.commit()

    # Явно загружаем связанные данные (categories), чтобы Pydantic мог их сериализовать
    await session.refresh(new_product, ["categories"])

    return new_product


async def update_product_data(
    session: AsyncSession, product_id: int, data: ProductUpdate
):
    product = await session.get(Product, product_id, options=[selectinload(Product.categories)])
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if data.title is not None:
        product.title = data.title
        product.slug = generate_slug(data.title)
    if data.description is not None:
        product.description = data.description
    if data.price is not None:
        product.price = data.price
    if data.stock_quantity is not None:
        product.stock_quantity = data.stock_quantity
    if data.gender is not None:
        product.gender = data.gender
    if data.size is not None:
        product.size = data.size
    if data.image_url is not None:
        product.image_url = data.image_url

    if data.category_ids is not None:
        if data.category_ids:
            stmt = select(Category).where(Category.id.in_(data.category_ids))
            result = await session.execute(stmt)
            product.categories = result.scalars().all()
        else:
            product.categories = []

    session.add(product)
    await session.commit()
    await session.refresh(product, ["categories"])
    return product


async def get_all_products(
    session: AsyncSession,
    category_names: list[str] | None = None,
    search: str | None = None,
    gender: str | None = None,
    size: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 20,
    page: int = 1,
):
    stmt = select(Product).options(selectinload(Product.categories))

    if category_names:
        stmt = stmt.join(Product.categories).where(Category.name.in_(category_names))

    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Product.title.ilike(search_pattern),
                Product.description.ilike(search_pattern),
            )
        )

    if gender:
        stmt = stmt.where(Product.gender == gender)

    if size:
        stmt = stmt.where(Product.size == size)

    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)

    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    # Подсчёт общего количества без дублирования при join
    count_stmt = stmt.with_only_columns(func.count(func.distinct(Product.id))).order_by(None)
    total = await session.scalar(count_stmt)

    stmt = stmt.distinct().limit(limit).offset((page - 1) * limit)

    result = await session.execute(stmt)
    products = result.scalars().all()

    return {"total": total, "page": page, "limit": limit, "items": products}


async def get_product_by_slug(session: AsyncSession, slug: str):
    stmt = (
        select(Product)
        .options(selectinload(Product.categories))
        .where(Product.slug == slug)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
