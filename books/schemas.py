from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Book Schemas
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    description: Optional[str] = None
    category: Optional[str] = None
    total_copies: int = 1
    available_copies: int = 1
    price: Decimal
    publication_year: Optional[int] = None
    is_active: bool = True

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
    price: Optional[Decimal] = None
    publication_year: Optional[int] = None
    is_active: Optional[bool] = None

class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Rental Schemas
class RentalBase(BaseModel):
    user_id: int
    book_id: int
    due_date: datetime
    daily_rate: Decimal

class RentalCreate(RentalBase):
    pass

class RentalUpdate(BaseModel):
    due_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    daily_rate: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    is_returned: Optional[bool] = None
    late_fee: Optional[Decimal] = None
    status: Optional[str] = None

class RentalResponse(RentalBase):
    id: int
    rental_date: datetime
    return_date: Optional[datetime] = None
    total_amount: Optional[Decimal] = None
    is_returned: bool
    late_fee: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Combined response with book details
class RentalWithBookResponse(RentalResponse):
    book: BookResponse
    
    class Config:
        from_attributes = True
