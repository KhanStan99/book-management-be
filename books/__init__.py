# Books module - Book rental management system

from .models import Book, Rental
from .schemas import (
    BookCreate, BookUpdate, BookResponse,
    RentalCreate, RentalUpdate, RentalResponse
)
from .crud import (
    create_book, get_books, get_book, update_book, delete_book,
    create_rental, get_rentals, return_book
)

__all__ = [
    # Models
    "Book", "Rental",
    # Schemas
    "BookCreate", "BookUpdate", "BookResponse",
    "RentalCreate", "RentalUpdate", "RentalResponse",
    # CRUD operations
    "create_book", "get_books", "get_book", "update_book", "delete_book",
    "create_rental", "get_rentals", "return_book",
]
