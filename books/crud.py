from sqlalchemy.orm import Session
from books.models import Book, Rental
from books.schemas import BookCreate, BookUpdate, RentalCreate, RentalUpdate
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from decimal import Decimal

# ============= BOOK CRUD OPERATIONS =============

def create_book(db: Session, book: BookCreate) -> Book:
    """Create a new book"""
    # Check if ISBN already exists
    db_book = db.query(Book).filter(Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book with this ISBN already exists"
        )
    
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_books(db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
    """Get all books with pagination"""
    return db.query(Book).filter(Book.is_active == True).offset(skip).limit(limit).all()

def get_book(db: Session, book_id: int) -> Book:
    """Get a specific book by ID"""
    db_book = db.query(Book).filter(Book.id == book_id, Book.is_active == True).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return db_book

def update_book(db: Session, book_id: int, book: BookUpdate) -> Book:
    """Update a book"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    update_data = book.dict(exclude_unset=True)
    
    # Check if ISBN is being updated and if it already exists
    if "isbn" in update_data:
        existing_book = db.query(Book).filter(
            Book.isbn == update_data["isbn"],
            Book.id != book_id
        ).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists"
            )
    
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db_book.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    """Soft delete a book"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if book has active rentals
    active_rentals = db.query(Rental).filter(
        Rental.book_id == book_id,
        Rental.is_returned == False
    ).first()
    
    if active_rentals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete book with active rentals"
        )
    
    db_book.is_active = False
    db.commit()

# ============= RENTAL CRUD OPERATIONS =============

def create_rental(db: Session, rental: RentalCreate) -> Rental:
    """Create a new rental"""
    # Check if book exists and is available
    db_book = db.query(Book).filter(Book.id == rental.book_id, Book.is_active == True).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if db_book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book is not available for rental"
        )
    
    # Check if user already has this book rented
    existing_rental = db.query(Rental).filter(
        Rental.user_id == rental.user_id,
        Rental.book_id == rental.book_id,
        Rental.is_returned == False
    ).first()
    
    if existing_rental:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this book rented"
        )
    
    # Create rental
    db_rental = Rental(**rental.dict())
    db.add(db_rental)
    
    # Update book availability
    db_book.available_copies -= 1
    
    db.commit()
    db.refresh(db_rental)
    return db_rental

def get_rentals(db: Session, skip: int = 0, limit: int = 100) -> List[Rental]:
    """Get all rentals"""
    return db.query(Rental).offset(skip).limit(limit).all()

def get_rental(db: Session, rental_id: int) -> Rental:
    """Get a specific rental by ID"""
    db_rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not db_rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    return db_rental

def get_user_rentals(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Rental]:
    """Get all rentals for a specific user"""
    return db.query(Rental).filter(Rental.user_id == user_id).offset(skip).limit(limit).all()

def return_book(db: Session, rental_id: int) -> Rental:
    """Return a rented book"""
    db_rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not db_rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )
    
    if db_rental.is_returned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book is already returned"
        )
    
    # Calculate total amount and late fee
    return_date = datetime.utcnow()
    rental_days = (return_date - db_rental.rental_date).days + 1
    
    total_amount = db_rental.daily_rate * rental_days
    late_fee = Decimal(0)
    
    if return_date > db_rental.due_date:
        late_days = (return_date - db_rental.due_date).days
        late_fee = db_rental.daily_rate * Decimal(0.5) * late_days  # 50% of daily rate as late fee
    
    # Update rental
    db_rental.return_date = return_date
    db_rental.total_amount = total_amount
    db_rental.late_fee = late_fee
    db_rental.is_returned = True
    db_rental.status = "returned"
    
    # Update book availability
    db_book = db.query(Book).filter(Book.id == db_rental.book_id).first()
    if db_book:
        db_book.available_copies += 1
    
    db.commit()
    db.refresh(db_rental)
    return db_rental

def get_overdue_rentals(db: Session) -> List[Rental]:
    """Get all overdue rentals"""
    current_date = datetime.utcnow()
    return db.query(Rental).filter(
        Rental.due_date < current_date,
        Rental.is_returned == False
    ).all()
