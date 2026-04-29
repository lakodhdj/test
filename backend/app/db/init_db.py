from app.db.base import Base
from app.db.config import engine, async_session
from sqlalchemy import select, func
from app.product.models import Category, Product
from app.product.utils import generate_slug


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

        # Check if products exist, if not add demo products
        products_count = await session.scalar(select(func.count(Product.id))) or 0
        if products_count == 0:
            # Get categories
            stmt = select(Category)
            result = await session.execute(stmt)
            categories_dict = {cat.name: cat for cat in result.scalars().all()}

            # Demo products
            demo_products = [
                Product(
                    title="Классическая черная куртка",
                    description="Стильная водоотталкивающая куртка для всех сезонов",
                    price=4990,
                    stock_quantity=15,
                    gender="unisex",
                    size="M",
                    slug=generate_slug("Классическая черная куртка"),
                    image_url="https://via.placeholder.com/300?text=Куртка",
                    categories=[categories_dict.get("Outerwear")] if "Outerwear" in categories_dict else []
                ),
                Product(
                    title="Premium T-Shirt",
                    description="Комфортная хлопковая футболка высокого качества",
                    price=1490,
                    stock_quantity=30,
                    gender="male",
                    size="L",
                    slug=generate_slug("Premium T-Shirt"),
                    image_url="https://via.placeholder.com/300?text=T-Shirt",
                    categories=[categories_dict.get("T-Shirts")] if "T-Shirts" in categories_dict else []
                ),
                Product(
                    title="Черные джинсы",
                    description="Классические черные джинсы прямого кроя",
                    price=2990,
                    stock_quantity=20,
                    gender="female",
                    size="S",
                    slug=generate_slug("Черные джинсы"),
                    image_url="https://via.placeholder.com/300?text=Jeans",
                    categories=[categories_dict.get("Jeans")] if "Jeans" in categories_dict else []
                ),
                Product(
                    title="Кроссовки Air Comfort",
                    description="Удобные спортивные кроссовки для повседневной носки",
                    price=5490,
                    stock_quantity=25,
                    gender="unisex",
                    size="M",
                    slug=generate_slug("Кроссовки Air Comfort"),
                    image_url="https://via.placeholder.com/300?text=Обувь",
                    categories=[categories_dict.get("Обувь")] if "Обувь" in categories_dict else []
                ),
                Product(
                    title="Спортивное платье",
                    description="Легкое платье для активного образа жизни",
                    price=3490,
                    stock_quantity=18,
                    gender="female",
                    size="M",
                    slug=generate_slug("Спортивное платье"),
                    image_url="https://via.placeholder.com/300?text=Платье",
                    categories=[categories_dict.get("Dresses")] if "Dresses" in categories_dict else []
                ),
                Product(
                    title="Спортивный костюм",
                    description="Комфортный костюм для тренировок",
                    price=3990,
                    stock_quantity=22,
                    gender="male",
                    size="L",
                    slug=generate_slug("Спортивный костюм"),
                    image_url="https://via.placeholder.com/300?text=Sportswear",
                    categories=[categories_dict.get("Sportswear")] if "Sportswear" in categories_dict else []
                ),
            ]
            
            session.add_all(demo_products)
            await session.commit()
            print(f"✅ Добавлено {len(demo_products)} демонстрационных товаров")

    print("✅ Таблицы созданы. Базовые категории и товары готовы.")
