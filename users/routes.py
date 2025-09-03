from fastapi import APIRouter, Depends, status
from auth.utils import get_current_user, create_access_token, create_refresh_token
from sqlalchemy.orm import Session
from users.crud import create_user, get_users, get_user, login_user, update_user, delete_user
from users.schemas import UserCreate, UserUpdate, UserResponse
from auth.schemas import LoginResponse
from database.dependency import get_db
from typing import List

router = APIRouter()

@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def api_create_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/users/login", response_model=LoginResponse)
def api_login_user(email: str, password: str, db: Session = Depends(get_db)):
    user = login_user(db, email, password)
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"email": user.email})
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active
        },
        refresh_token=refresh_token
    )

@router.get("/users/", response_model=List[UserResponse])
def api_get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_users(db, skip, limit)

@router.get("/users/{user_id}", response_model=UserResponse)
def api_get_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_user(db, user_id)

@router.put("/users/{user_id}", response_model=UserResponse)
def api_update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return update_user(db, user_id, user)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return delete_user(db, user_id)
