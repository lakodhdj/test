from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.base import Base

wishlist_table = Table(
    "wishlist",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "product_id",
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
