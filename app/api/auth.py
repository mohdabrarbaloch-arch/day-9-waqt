"""Authentication endpoints: register, login, me."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas.waqt import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
limiter = Limiter(key_func=get_remote_address)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    subject = decode_access_token(token)
    if subject is None:
        raise credentials_error
    user = db.get(User, int(subject))
    if user is None:
        raise credentials_error
    return user


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email.lower(),
        name=payload.name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        expires_in_minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        expires_in_minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES,
    )


@router.get("/me", response_model=UserResponse)
def me(current: User = Depends(get_current_user)):
    return current
