"""
FastAPI dependencies for authentication.

Logout with stateless JWT: a JWT can't be un-issued, so logout here revokes
the token by adding it to a blocklist checked on every request. This
in-memory set is fine for a single-process competition/demo deployment;
production with multiple workers should back this with Redis (documented
in README limitations) so all workers share the same blocklist.
"""
from __future__ import annotations
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, TokenError
from app.models.db import get_db
from app.models.orm import User

security_scheme = HTTPBearer(auto_error=False)
_REVOKED_TOKENS: set[str] = set()


def revoke_token(token: str) -> None:
    _REVOKED_TOKENS.add(token)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    if token in _REVOKED_TOKENS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    try:
        payload = decode_access_token(token)
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    """For endpoints that work anonymously but personalize when logged in
    (e.g. demo prediction endpoint used by judges without an account)."""
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
