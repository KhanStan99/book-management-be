from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from auth.schemas import LoginRequest, LoginResponse
from auth.utils import create_access_token, get_current_user, verify_token, create_refresh_token
from users.crud import login_user
from database.dependency import get_db
from users.schemas import UserResponse
from jose import JWTError

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def api_login_user(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = login_user(db, login_req.email, login_req.password)
    print("user:", user)
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

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: Request):
    data = await request.json()
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token required")
    try:
        payload = verify_token(refresh_token, allow_expired=True, is_refresh=True)
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        new_access_token = create_access_token({"sub": email})
        return LoginResponse(
            access_token=new_access_token,
            token_type="bearer",
            user={"email": email}
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
