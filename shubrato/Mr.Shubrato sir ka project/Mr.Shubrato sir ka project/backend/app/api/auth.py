"""
SAATHI authentication routes.

Endpoints
---------
POST /auth/register   – Create a new user account (name, phone, parent_phone, password)
POST /auth/login      – Authenticate with phone + password, returns session token
POST /auth/logout     – Invalidate the current session token
GET  /auth/me         – Return current user info from session token header

Security
--------
* Passwords are hashed with PBKDF2-HMAC-SHA256 (Python built-in hashlib — no extra deps).
* Session tokens are 32-byte cryptographically random hex strings.
* Sessions expire after 24 hours.
* Duplicate phone registrations return HTTP 409 (Conflict).
* Wrong phone/password always returns the same HTTP 401 (no user-enumeration via timing).
"""

import hashlib
import os
from datetime import datetime, timedelta, timezone
from secrets import token_hex

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import User, UserSession
from app.schemas.api import TokenOut, UserLogin, UserOut, UserRegister

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

# Session lifetime
_SESSION_TTL_HOURS = 24


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _hash_password(plain: str, salt: str) -> str:
    """Return a PBKDF2-HMAC-SHA256 hex digest of *plain* using *salt*."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        plain.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=260_000,
    ).hex()


def _make_salt() -> str:
    """Return a fresh 32-byte random hex salt."""
    return os.urandom(32).hex()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _get_user_from_token(
    authorization: str = Header(
        default=None,
        alias="Authorization",
        description="Bearer <session-token>",
    ),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: parse the Authorization header, look up the session,
    and return the associated User, or raise HTTP 401.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Use 'Bearer <token>'.",
        )
    raw_token = authorization[len("Bearer "):].strip()
    session = db.query(UserSession).filter(UserSession.token == raw_token).first()
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token.")
    now = _utcnow()
    if session.expires_at.replace(tzinfo=timezone.utc) < now:
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session has expired. Please log in again.")
    user = db.get(User, session.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return user


def _build_token_response(user: User, db: Session) -> TokenOut:
    """Create a new session for *user* and return a TokenOut."""
    now = _utcnow()
    expires_at = now + timedelta(hours=_SESSION_TTL_HOURS)
    session = UserSession(
        token=token_hex(32),
        user_id=user.id,
        created_at=now,
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return TokenOut(
        token=session.token,
        user=UserOut.model_validate(user),
        expires_at=expires_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@auth_router.post(
    "/register",
    response_model=TokenOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        409: {"description": "Phone number already registered"},
        422: {"description": "Validation error"},
    },
)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Create a new SAATHI user account.

    * **name** – display name (2–160 chars)
    * **phone** – unique mobile number used as login ID
    * **parent_phone** – optional parent / guardian number
    * **password** – minimum 6 characters (stored as PBKDF2 hash, never plain-text)

    Returns a session token on success.
    """
    # Normalise phone for uniqueness check
    phone = payload.phone.strip()
    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this phone number is already registered.",
        )

    salt = _make_salt()
    hashed = _hash_password(payload.password, salt)

    user = User(
        name=payload.name.strip(),
        phone=phone,
        parent_phone=payload.parent_phone.strip() if payload.parent_phone else None,
        password_hash=hashed,
        password_salt=salt,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _build_token_response(user, db)


@auth_router.post(
    "/login",
    response_model=TokenOut,
    summary="Log in with phone and password",
    responses={
        401: {"description": "Invalid credentials"},
    },
)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate with phone number and password.

    Returns a session token valid for 24 hours.  Store it client-side and
    send it in the ``Authorization: Bearer <token>`` header for protected requests.
    """
    phone = payload.phone.strip()
    user = db.query(User).filter(User.phone == phone).first()

    # Always hash so timing is the same whether user exists or not
    dummy_salt = "0" * 64
    candidate_hash = _hash_password(
        payload.password,
        user.password_salt if user else dummy_salt,
    )
    if user is None or candidate_hash != user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password.",
        )

    return _build_token_response(user, db)


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out (invalidate session token)",
)
def logout(
    authorization: str = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    """
    Invalidate the current session token.

    The client should delete the token from local storage after calling this.
    """
    if authorization and authorization.startswith("Bearer "):
        raw_token = authorization[len("Bearer "):].strip()
        session = db.query(UserSession).filter(UserSession.token == raw_token).first()
        if session:
            db.delete(session)
            db.commit()


@auth_router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user info",
    responses={401: {"description": "Not authenticated"}},
)
def me(user: User = Depends(_get_user_from_token)):
    """
    Return the user record for the currently authenticated session.

    Requires ``Authorization: Bearer <token>`` header.
    """
    return user
