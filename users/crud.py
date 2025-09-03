from sqlalchemy.orm import Session
from users.models import User
from users.schemas import UserCreate, UserUpdate
from typing import List
from fastapi import HTTPException, status
from datetime import datetime
from auth.password import get_password_hash, verify_password

# CREATE - Create a new user
def create_user(db: Session, user: UserCreate) -> User:
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=get_password_hash(user.password),
        age=user.age,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Login - login user
def login_user(db: Session, email: str, password: str) -> User:
    db_user = db.query(User).filter(User.email == email).first()
    if db_user is None or not verify_password(password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return db_user

# READ - Get all users
def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

# READ - Get a specific user by ID
def get_user(db: Session, user_id: int) -> User:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

# UPDATE - Update a user
def update_user(db: Session, user_id: int, user: UserUpdate) -> User:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    update_data = user.dict(exclude_unset=True)
    if "email" in update_data:
        existing_user = db.query(User).filter(
            User.email == update_data["email"],
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

# DELETE - Delete a user
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(db_user)
    db.commit()
