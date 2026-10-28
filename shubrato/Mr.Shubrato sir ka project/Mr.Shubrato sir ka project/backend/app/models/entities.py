"""
SAATHI SQLAlchemy database models (entities).

Five tables are used:
  - support_services   : directory of support providers (seeded; not verified)
  - hazard_reports     : public-space safety reports submitted by users
  - support_requests   : private support-category preferences submitted by users
  - users              : registered user accounts (phone-based login)
  - user_sessions      : session tokens for authenticated users

All timestamps are stored timezone-aware (UTC).
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def _utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Support-service directory
# ---------------------------------------------------------------------------

class SupportService(Base):
    """
    A directory entry for a support provider.

    All seed entries have ``verified=False`` and are explicitly presented as
    demo / illustrative records, not live-verified referrals.
    """
    __tablename__ = "support_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    website: Mapped[str | None] = mapped_column(String(300), nullable=True)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    city: Mapped[str] = mapped_column(String(100), default="Nagpur")
    accessibility_notes: Mapped[str] = mapped_column(
        Text, default="Contact the provider to confirm current accessibility."
    )
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_verified: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


# ---------------------------------------------------------------------------
# Hazard reports
# ---------------------------------------------------------------------------

class HazardReport(Base):
    """
    A public-space safety hazard report submitted anonymously by a user.

    Coordinates (latitude/longitude) are stored but intentionally excluded from
    every API response schema to prevent location exposure.
    """
    __tablename__ = "hazard_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reference_code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location_text: Mapped[str] = mapped_column(String(300), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="received")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


# ---------------------------------------------------------------------------
# Support preference / request
# ---------------------------------------------------------------------------

class SupportRequest(Base):
    """
    A private support-category preference saved by a user.

    There is deliberately no public GET endpoint.  The reference code is
    returned only in the 201 creation response and cannot be looked up later,
    so third parties cannot read a submission by guessing reference codes.
    """
    __tablename__ = "support_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reference_code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    support_type: Mapped[str] = mapped_column(String(60), nullable=False)
    preferred_contact: Mapped[str] = mapped_column(
        String(40), default="self-directed"
    )
    message: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="received")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


# ---------------------------------------------------------------------------
# User accounts
# ---------------------------------------------------------------------------

class User(Base):
    """
    A registered user account.

    Phone number is used as the unique login identifier.
    Passwords are stored as PBKDF2-HMAC-SHA256 hashes (never plain-text).
    Parent phone is optional contact information, stored for emergency context.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    parent_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    password_salt: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


# ---------------------------------------------------------------------------
# User sessions
# ---------------------------------------------------------------------------

class UserSession(Base):
    """
    A session token for an authenticated user.

    Tokens are 32-byte random hex strings (64 hex chars).
    Sessions expire 24 hours after creation.
    """
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
