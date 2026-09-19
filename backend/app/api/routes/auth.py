from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.db import get_db
from app.models.orm import User
from app.api.deps import get_current_user, security_scheme, revoke_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new account",
             responses={409: {"description": "Email already registered"}})
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        organization=payload.organization,
        role="viewer",
        is_active=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse,
             summary="Log in and receive a JWT access token",
             responses={401: {"description": "Incorrect email or password"}})
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        # Deliberately identical error for "no such user" and "wrong password"
        # so the API doesn't leak which emails are registered.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    token = create_access_token(subject=str(user.id), extra_claims={"role": user.role})
    return TokenResponse(access_token=token, expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


@router.post("/logout", summary="Revoke the current access token")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
           current_user: User = Depends(get_current_user)):
    revoke_token(credentials.credentials)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse, summary="Get the current authenticated user")
def me(current_user: User = Depends(get_current_user)):
    return current_user
