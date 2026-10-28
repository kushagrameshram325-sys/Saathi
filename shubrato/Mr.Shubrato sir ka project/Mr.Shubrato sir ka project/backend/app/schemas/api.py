"""
SAATHI Pydantic request/response schemas.

Design rules
------------
* ServiceOut, HazardOut, SupportRequestOut are ORM-mode models (from_attributes=True).
* HazardOut deliberately omits latitude/longitude – coordinates must never be
  returned in public API responses.
* SupportRequestOut deliberately omits 'message' – the submitted narrative is
  stored but not echoed back to prevent accidental exposure.
* SupportRequestCreate requires consent=True; the route enforces this, but
  the field-level validation (using a validator) provides a clear schema hint.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Support-service directory
# ---------------------------------------------------------------------------

class ServiceOut(BaseModel):
    """Public representation of a support-service directory entry."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    description: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: str
    accessibility_notes: str
    verified: bool
    last_verified: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Hazard reports
# ---------------------------------------------------------------------------

class HazardCreate(BaseModel):
    """Payload for creating a new public-space hazard report."""
    category: str = Field(
        min_length=2,
        max_length=60,
        description="Hazard category slug, e.g. 'streetlight', 'harassment', 'footpath'.",
        examples=["streetlight"],
    )
    description: str = Field(
        min_length=5,
        max_length=2000,
        description="Plain-language description of the hazard.",
        examples=["Streetlight appears to be broken on the footpath near the bus stop."],
    )
    location_text: str = Field(
        min_length=2,
        max_length=300,
        description="Human-readable location reference.",
        examples=["Near the main bus stop, MG Road"],
    )
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
        description="Optional GPS latitude. Stored but never returned in API responses.",
    )
    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
        description="Optional GPS longitude. Stored but never returned in API responses.",
    )

    @field_validator("category", "description", "location_text", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class HazardOut(BaseModel):
    """
    Public representation of a hazard report.

    Latitude and longitude are intentionally absent – they are stored in the
    database but must not be returned in any response.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_code: str
    category: str
    description: str
    location_text: str
    status: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Support preference / request
# ---------------------------------------------------------------------------

class SupportRequestCreate(BaseModel):
    """Payload for saving a private support preference."""
    support_type: str = Field(
        min_length=2,
        max_length=60,
        description="Support category, e.g. 'counselling', 'legal-support', 'shelter'.",
        examples=["counselling"],
    )
    preferred_contact: str = Field(
        default="self-directed",
        max_length=40,
        description="Preferred follow-up method, e.g. 'self-directed', 'phone', 'chat'.",
        examples=["self-directed"],
    )
    message: str = Field(
        default="",
        max_length=2000,
        description="Optional free-text note. Stored in the database; not returned in responses.",
        examples=["Please show information about available options."],
    )
    consent: bool = Field(
        description=(
            "Must be true. Confirms the user understands that this demo stores "
            "submitted information in the local database and does not contact providers."
        )
    )

    @field_validator("support_type", "preferred_contact", "message", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class SupportRequestOut(BaseModel):
    """
    Response returned after a support preference is saved.

    The 'message' field is intentionally omitted; the submitted narrative is
    not echoed back in any response.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_code: str
    support_type: str
    preferred_contact: str
    status: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Auth: Register / Login
# ---------------------------------------------------------------------------

class UserRegister(BaseModel):
    """Payload for creating a new user account."""
    name: str = Field(
        min_length=2,
        max_length=160,
        description="Full name of the user.",
        examples=["Priya Sharma"],
    )
    phone: str = Field(
        min_length=7,
        max_length=20,
        description="Mobile phone number used as the login identifier.",
        examples=["9876543210"],
    )
    parent_phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Parent or guardian phone number (optional).",
        examples=["9123456789"],
    )
    password: str = Field(
        min_length=6,
        max_length=128,
        description="Password (min 6 characters). Stored as a salted hash; never plain-text.",
    )

    @field_validator("name", "phone", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class UserLogin(BaseModel):
    """Payload for authenticating with phone + password."""
    phone: str = Field(
        min_length=7,
        max_length=20,
        description="Registered phone number.",
        examples=["9876543210"],
    )
    password: str = Field(
        min_length=1,
        max_length=128,
        description="Account password.",
    )


class UserOut(BaseModel):
    """Public representation of a user account (no password fields)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    parent_phone: Optional[str] = None
    created_at: datetime


class TokenOut(BaseModel):
    """Response returned on successful login or registration."""
    token: str
    user: UserOut
    expires_at: datetime
