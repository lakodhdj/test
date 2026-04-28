from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    UploadFile,
    Form,
    File,
)
from app.account.models import User
from app.db.config import SessionDep
from app.account.deps import require_admin

# ←←← ИМПОРТЫ СХЕМ ←←←
from app.product.schemas import (
    ProductCreate,
    ProductOut,
    PaginatedProductOut,
    ProductUpdate,
    Gender,
    Size,
)

from app.product.services import (
    create_product,
    get_all_products,
    get_product_by_slug,
    update_product_data,
)


router = APIRouter(tags=["Products"])


@router.post("/", response_model=ProductOut)
async def product_create(
    session: SessionDep,
    title: str = Form(...),
    description: str | None = Form(None),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    gender: Gender = Form(...),
    size: Size = Form(...),
    category_ids: Annotated[list[int] | None, Form()] = [],
    image_url: str | None = Form(None),
    image_file: UploadFile | None = File(None),
    admin_user: User = Depends(require_admin),
):
    data = ProductCreate(
        title=title,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        gender=gender,
        size=size,
        category_ids=category_ids,
        image_url=image_url,
    )

    return await create_product(session, data, image_file)


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    session: SessionDep,
    product_update: ProductUpdate,
    admin_user: User = Depends(require_admin),
):
    updated = await update_product_data(session, product_id, product_update)
    return updated


@router.get("", response_model=PaginatedProductOut)
async def list_products(
    session: SessionDep,
    categories: list[str] | None = Query(default=None),
    search: str | None = Query(default=None),
    gender: str | None = Query(default=None),
    size: str | None = Query(default=None),
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
):
    return await get_all_products(
        session,
        category_names=categories,
        search=search,
        gender=gender,
        size=size,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        page=page,
    )


@router.get("/{slug}", response_model=ProductOut)
async def product_get_by_slug(session: SessionDep, slug: str):
    product = await get_product_by_slug(session, slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product
