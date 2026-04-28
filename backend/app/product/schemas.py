from pydantic import BaseModel, Field
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNISEX = "unisex"


class Size(str, Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"
    XXXL = "XXXL"


######################## Category ########################


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    name: str
    model_config = {"from_attributes": True}


######################## Product ########################


class ProductBase(BaseModel):
    title: str
    description: str | None = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(0, ge=0)
    gender: Gender  # ← добавлено
    size: Size  # ← добавлено
    image_url: str | None = None


class ProductCreate(ProductBase):
    category_ids: list[int] | None = None


class ProductOut(ProductBase):
    id: int
    slug: str
    image_url: str | None = None
    categories: list[CategoryOut] = []

    model_config = {"from_attributes": True}


class PaginatedProductOut(BaseModel):
    total: int
    page: int
    limit: int
    items: list[ProductOut]


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    stock_quantity: int | None = None
    image_url: str | None = None
    category_ids: list[int] | None = None
    gender: Gender | None = None  # ← добавлено
    size: Size | None = None  # ← добавлено
    model_config = {"from_attributes": True}
