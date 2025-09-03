from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from auth.schemas import LoginRequest, LoginResponse
from auth.utils import authenticate_user, create_access_token, get_current_user, verify_token
from database.dependency import get_db
from users.schemas import UserResponse
from jose import JWTError

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active
        }
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
