"""
ClimateGuard AI — Security utilities
========================================
Password hashing: PBKDF2-HMAC-SHA256, 260,000 iterations, per-user random
salt (Python's hashlib is a stdlib zero-dependency choice — NIST SP 800-132
approved KDF family, the same algorithm class Django uses by default).
bcrypt/argon2 via passlib are equally valid; if you'd rather standardize on
one of those in production, swap `hash_password`/`verify_password` below —
callers never see the underlying scheme.

JWT: PyJWT, HS256, secret from SECRET_KEY env var (never hardcoded).
"""
from __future__ import annotations
import os
import hmac
import hashlib
import secrets
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

PBKDF2_ITERATIONS = 260_000
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Dev-only fallback so the app boots locally without extra setup —
    # ALWAYS set a real SECRET_KEY via environment variable in production.
    SECRET_KEY = "dev-only-insecure-secret-change-me-" + secrets.token_hex(8)
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def hash_password(plain_password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(derived).decode()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        scheme, iterations, salt_b64, hash_b64 = stored_hash.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        derived = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt, int(iterations)
        )
        return hmac.compare_digest(derived, expected)
    except (ValueError, AttributeError):
        return False


def create_access_token(subject: str, extra_claims: Optional[dict] = None,
                         expires_minutes: Optional[int] = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "iat": now, "exp": expire, "type": "access"}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


class TokenError(Exception):
    pass


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise TokenError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise TokenError("Invalid token")
