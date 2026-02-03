from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class ProductCreate(BaseModel):
    name: str
    product_type: str
    market_value: Optional[float] = None
    description: Optional[str] = None
    images_url: Optional[str] = None
    set_name: Optional[str] = None
    release_date: Optional[date] = None

class Product(ProductCreate):
    id: str
    created_at: datetime
    last_updated: datetime

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class Category(CategoryCreate):
    id: int

class ItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    purchase_price: float = Field(ge=0)
    category_id: Optional[int] = None
    purchase_date: Optional[date] = None

class Item(BaseModel):
    id: int
    product_id: str
    category_id: Optional[int] = None
    quantity: int
    purchase_price: float
    purchase_date: date
    created_at: datetime
    updated_at: datetime

