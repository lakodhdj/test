from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Table,
    Column,
    Text,
    Enum as SQLEnum,
)
from datetime import datetime, timezone
import enum

from app.db.base import Base
from app.wishlist.wishlist import (
    wishlist_table,
)  # если у тебя файл называется wishlist.py


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    UNISEX = "unisex"


class Size(str, enum.Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"
    XXXL = "XXXL"


product_category_table = Table(
    "product_category",
    Base.metadata,
    Column(
        "product_id",
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(default=0)

    # Новые поля для магазина одежды
    gender: Mapped[Gender] = mapped_column(SQLEnum(Gender), nullable=False)
    size: Mapped[Size] = mapped_column(SQLEnum(Size), nullable=False)

    image_url: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Связи
    categories: Mapped[list["Category"]] = relationship(
        "Category", secondary=product_category_table, back_populates="products"
    )

    wishlisted_by: Mapped[list["User"]] = relationship(
        "User", secondary=wishlist_table, back_populates="wishlist"
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    products: Mapped[list["Product"]] = relationship(
        "Product", secondary=product_category_table, back_populates="categories"
    )
