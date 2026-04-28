from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускается при старте приложения
    print("🚀 Запуск приложения...")
    await init_db()
    yield
    # Здесь можно добавить очистку при выключении
    print("🛑 Приложение остановлено")


app = FastAPI(lifespan=lifespan)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8001",
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
from app.account.routers import router as account_router
from app.product.routers.category import router as category_router
from app.product.routers.product import router as product_router
from app.wishlist.routers import router as wishlist_router
from app.order.routers import router as order_router
from app.cart.routers import router as cart_router

app.include_router(account_router, prefix="/account")
app.include_router(category_router, prefix="/product/categories")
app.include_router(product_router, prefix="/product")
app.include_router(wishlist_router, prefix="/wishlist")
app.include_router(cart_router, prefix="/cart")
app.include_router(order_router, prefix="/orders")


@app.get("/")
async def root():
    return {"message": "E-commerce API is running"}
