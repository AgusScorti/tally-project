"""
Routes - Autenticación (login, registro, refresh token)
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, LoginRequest, Token, UserResponse
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_active_user,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# ==================== REGISTRO ====================

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario
    
    ```json
    {
      "email": "user@example.com",
      "username": "username",
      "full_name": "Full Name",
      "password": "secure_password_min_8_chars"
    }
    ```
    """
    # Verificar si el email ya existe
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verificar si el username ya existe
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Crear usuario
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# ==================== LOGIN ====================

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login con email y password
    
    ```json
    {
      "email": "user@example.com",
      "password": "password"
    }
    ```
    
    Devuelve JWT token
    """
    # Buscar usuario
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verificar password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# ==================== GET CURRENT USER ====================

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Obtener datos del usuario actual"""
    return current_user
