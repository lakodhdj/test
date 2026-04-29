from app.db.base import Base
from app.db.config import engine, async_session
from sqlalchemy import select, func
from app.product.models import Category


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Keep product data API-driven, but ensure base categories exist for admin UI/filtering.
    default_categories = [
        "Outerwear",
        "T-Shirts",
        "Jeans",
        "Обувь",
        "Accessories",
        "Dresses",
        "Sportswear",
    ]

    async with async_session() as session:
        categories_count = await session.scalar(select(func.count(Category.id))) or 0
        if categories_count == 0:
            session.add_all([Category(name=name) for name in default_categories])
            await session.commit()

    print("✅ Таблицы созданы. Базовые категории готовы, товары добавляются через API.")
