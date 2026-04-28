from sqlalchemy import select, func
from app.db.base import Base
from app.db.config import engine, async_session
from app.product.models import Product, Category, Gender, Size
from app.product.utils import generate_slug
from app.account.models import User
from app.account.utils import hash_password


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        category_count = await session.scalar(select(func.count(Category.id)))
        product_count = await session.scalar(select(func.count(Product.id)))

        if category_count == 0:
            categories = [
                Category(name=name)
                for name in [
                    "Outerwear",
                    "T-Shirts",
                    "Jeans",
                    "Shoes",
                    "Accessories",
                    "Dresses",
                    "Sportswear",
                ]
            ]
            session.add_all(categories)
            await session.commit()
            categories = (await session.execute(select(Category))).scalars().all()
        else:
            categories = (await session.execute(select(Category))).scalars().all()

        if product_count == 0:
            category_map = {category.name: category for category in categories}
            sample_products = [
                {
                    "title": "Classic Blue Denim Jacket",
                    "description": "Удобная джинсовая куртка в классическом стиле для ежедневной носки.",
                    "price": 89.99,
                    "stock_quantity": 18,
                    "gender": Gender.UNISEX,
                    "size": Size.M,
                    "category_names": ["Outerwear", "Jeans"],
                },
                {
                    "title": "White Cotton T-Shirt",
                    "description": "Лёгкая хлопковая футболка с универсальным кроем и комфортом на весь день.",
                    "price": 19.99,
                    "stock_quantity": 35,
                    "gender": Gender.UNISEX,
                    "size": Size.M,
                    "category_names": ["T-Shirts"],
                },
                {
                    "title": "Slim Fit Black Jeans",
                    "description": "Стильные чёрные джинсы с узким кроем и комфортной посадкой.",
                    "price": 64.99,
                    "stock_quantity": 22,
                    "gender": Gender.MALE,
                    "size": Size.L,
                    "category_names": ["Jeans"],
                },
                {
                    "title": "Summer Midi Dress",
                    "description": "Женственное платье длины миди с лёгкой тканью и воздушным силуэтом.",
                    "price": 54.99,
                    "stock_quantity": 14,
                    "gender": Gender.FEMALE,
                    "size": Size.S,
                    "category_names": ["Dresses"],
                },
                {
                    "title": "Grey Unisex Hoodie",
                    "description": "Тёплая толстовка-худи с мягкой внутренней отделкой и большим карманом.",
                    "price": 42.5,
                    "stock_quantity": 27,
                    "gender": Gender.UNISEX,
                    "size": Size.XL,
                    "category_names": ["Sportswear"],
                },
                {
                    "title": "Brown Leather Belt",
                    "description": "Классический кожаный ремень для джинсов и рубашек.",
                    "price": 29.5,
                    "stock_quantity": 40,
                    "gender": Gender.UNISEX,
                    "size": Size.M,
                    "category_names": ["Accessories"],
                },
                {
                    "title": "Navy Polo Shirt",
                    "description": "Поло из мягкого хлопка с аккуратным воротником и стильным тёмно-синим цветом.",
                    "price": 31.99,
                    "stock_quantity": 21,
                    "gender": Gender.MALE,
                    "size": Size.L,
                    "category_names": ["T-Shirts"],
                },
                {
                    "title": "Pink Silk Scarf",
                    "description": "Красивая шёлковая бирюзовая шаль для элегантных образов.",
                    "price": 24.99,
                    "stock_quantity": 16,
                    "gender": Gender.FEMALE,
                    "size": Size.S,
                    "category_names": ["Accessories"],
                },
                {
                    "title": "Green Cargo Shorts",
                    "description": "Удобные карго-шорты с большим количеством карманов для прогулки и отдыха.",
                    "price": 34.99,
                    "stock_quantity": 19,
                    "gender": Gender.UNISEX,
                    "size": Size.M,
                    "category_names": ["Sportswear"],
                },
                {
                    "title": "White Leather Sneakers",
                    "description": "Светлые кроссовки из экокожи для повседневного стиля.",
                    "price": 74.99,
                    "stock_quantity": 24,
                    "gender": Gender.UNISEX,
                    "size": Size.L,
                    "category_names": ["Shoes"],
                },
                {
                    "title": "Soft Knit Sweater",
                    "description": "Тёплый джемпер из мягкого трикотажа для комфортной осенней носки.",
                    "price": 49.99,
                    "stock_quantity": 17,
                    "gender": Gender.FEMALE,
                    "size": Size.M,
                    "category_names": ["Outerwear"],
                },
                {
                    "title": "Denim Mini Skirt",
                    "description": "Короткая юбка из денима для яркого летнего образа.",
                    "price": 38.99,
                    "stock_quantity": 12,
                    "gender": Gender.FEMALE,
                    "size": Size.S,
                    "category_names": ["Dresses"],
                },
                {
                    "title": "Graphic Statement Tee",
                    "description": "Футболка с графическим принтом для смелых модных образов.",
                    "price": 22.0,
                    "stock_quantity": 31,
                    "gender": Gender.UNISEX,
                    "size": Size.XL,
                    "category_names": ["T-Shirts"],
                },
                {
                    "title": "Classic Chino Pants",
                    "description": "Строгие чиносы в офисном и повседневном стиле.",
                    "price": 52.0,
                    "stock_quantity": 20,
                    "gender": Gender.MALE,
                    "size": Size.L,
                    "category_names": ["Jeans"],
                },
                {
                    "title": "Baseball Cap",
                    "description": "Классическая бейсболка для солнечных дней и активного отдыха.",
                    "price": 15.5,
                    "stock_quantity": 44,
                    "gender": Gender.UNISEX,
                    "size": Size.M,
                    "category_names": ["Accessories"],
                },
                {
                    "title": "Striped Long Sleeve Shirt",
                    "description": "Лёгкая рубашка в полоску для деловых и повседневных образов.",
                    "price": 36.5,
                    "stock_quantity": 18,
                    "gender": Gender.FEMALE,
                    "size": Size.M,
                    "category_names": ["T-Shirts"],
                },
                {
                    "title": "Black Leather Wallet",
                    "description": "Удобный кошелек из натуральной кожи для карт и наличных.",
                    "price": 27.0,
                    "stock_quantity": 29,
                    "gender": Gender.UNISEX,
                    "size": Size.M,
                    "category_names": ["Accessories"],
                },
                {
                    "title": "Oversized Sweatshirt",
                    "description": "Свободный свитшот с модным кроем и мягким утеплителем.",
                    "price": 45.5,
                    "stock_quantity": 25,
                    "gender": Gender.UNISEX,
                    "size": Size.XXL,
                    "category_names": ["Sportswear"],
                },
                {
                    "title": "Travel Backpack",
                    "description": "Прочный рюкзак для поездок и учебы с несколькими отделениями.",
                    "price": 59.99,
                    "stock_quantity": 28,
                    "gender": Gender.UNISEX,
                    "size": Size.L,
                    "category_names": ["Accessories"],
                },
            ]

            query_map = {
                "Outerwear": "jacket",
                "T-Shirts": "tshirt",
                "Jeans": "jeans",
                "Shoes": "shoes",
                "Accessories": "accessory",
                "Dresses": "dress",
                "Sportswear": "sportswear",
            }

            products = []
            for item in sample_products:
                slug = generate_slug(item["title"])
                query_terms = ",".join({query_map.get(name, "clothing") for name in item["category_names"]})
                image_url = f"https://source.unsplash.com/600x400/?fashion,clothing,{query_terms}"
                product = Product(
                    title=item["title"],
                    description=item["description"],
                    slug=slug,
                    price=item["price"],
                    stock_quantity=item["stock_quantity"],
                    gender=item["gender"],
                    size=item["size"],
                    image_url=image_url,
                    categories=[category_map[name] for name in item["category_names"]],
                )
                products.append(product)

            session.add_all(products)
            await session.commit()
        else:
            products = (await session.execute(select(Product))).scalars().all()
            for product in products:
                if not product.image_url or 'picsum.photos' in product.image_url:
                    product.image_url = f"https://source.unsplash.com/600x400/?fashion,clothing,{product.slug}"
            await session.commit()

        admin_exists = await session.scalar(select(func.count(User.id)).where(User.is_admin == True))
        if not admin_exists:
            admin_user = User(
                email="admin@example.com",
                hashed_password=hash_password("Admin1234"),
                is_admin=True,
                is_verified=True,
            )
            session.add(admin_user)
            await session.commit()

    print("✅ Все таблицы успешно созданы и заполнены начальными товарами")
