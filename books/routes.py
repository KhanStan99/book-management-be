from fastapi import APIRouter, Depends, status
from auth.utils import get_current_user
from sqlalchemy.orm import Session
from books.crud import (
    create_book, get_books, get_book, update_book, delete_book,
    create_rental, get_rentals, get_rental, get_user_rentals, 
    return_book, get_overdue_rentals
)
from books.schemas import (
    BookCreate, BookUpdate, BookResponse,
    RentalCreate, RentalUpdate, RentalResponse, RentalWithBookResponse
)
from database.dependency import get_db
from typing import List

router = APIRouter()

# ============= BOOK ROUTES =============

@router.post("/books/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def api_create_book(book: BookCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Create a new book"""
    return create_book(db, book)

@router.get("/books/", response_model=List[BookResponse])
def api_get_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all books"""
    return get_books(db, skip, limit)

@router.get("/books/{book_id}", response_model=BookResponse)
def api_get_book(book_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get a specific book"""
    return get_book(db, book_id)

@router.put("/books/{book_id}", response_model=BookResponse)
def api_update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Update a book"""
    return update_book(db, book_id, book)

@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_book(book_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Delete a book"""
    return delete_book(db, book_id)

# ============= RENTAL ROUTES =============

@router.post("/rentals/", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def api_create_rental(rental: RentalCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Create a new rental"""
    return create_rental(db, rental)

@router.get("/rentals/", response_model=List[RentalResponse])
def api_get_rentals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all rentals"""
    return get_rentals(db, skip, limit)

@router.get("/rentals/{rental_id}", response_model=RentalResponse)
def api_get_rental(rental_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get a specific rental"""
    return get_rental(db, rental_id)

@router.get("/users/{user_id}/rentals", response_model=List[RentalResponse])
def api_get_user_rentals(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all rentals for a specific user"""
    return get_user_rentals(db, user_id, skip, limit)

@router.put("/rentals/{rental_id}/return", response_model=RentalResponse)
def api_return_book(rental_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Return a rented book"""
    return return_book(db, rental_id)

@router.get("/rentals/overdue", response_model=List[RentalResponse])
def api_get_overdue_rentals(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all overdue rentals"""
    return get_overdue_rentals(db)
