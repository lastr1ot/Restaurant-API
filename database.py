from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession

class Base(DeclarativeBase):
    pass

class OrderDB(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(Integer)
    items: Mapped[str] = mapped_column(Text)
    total_price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default="new")