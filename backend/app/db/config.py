from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import Depends
from typing import AsyncGenerator, Annotated
from decouple import config

# Настройки из .env
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST", default="db")  # имя сервиса в docker-compose
DB_NAME = config("DB_NAME")
DB_PORT = config("DB_PORT", cast=int, default=5432)
DATABASE_URL = config("DATABASE_URL", default=None)

if not DATABASE_URL:
    DATABASE_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# Создаём движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # В продакшене лучше False, в dev можно True
    future=True,
    pool_pre_ping=True,  # Полезно в Docker (проверяет соединение)
)

# Фабрика сессий
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


# Dependency для FastAPI
SessionDep = Annotated[AsyncSession, Depends(get_session)]
