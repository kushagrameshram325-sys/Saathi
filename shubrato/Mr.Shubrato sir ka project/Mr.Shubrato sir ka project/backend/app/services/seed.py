"""
SAATHI seed data for the support-service directory.

All entries are explicitly flagged as demo / unverified records.
They serve as illustrative listings only and must not be used as live referrals
before replacement with locally verified, maintained information.
"""

from sqlalchemy.orm import Session

from app.models.entities import SupportService

# ---------------------------------------------------------------------------
# Demo service listings (not verified)
# ---------------------------------------------------------------------------

DEMO_SERVICES: list[dict] = [
    {
        "name": "Women Helpline 181",
        "category": "helpline",
        "description": (
            "Government women-support helpline information. "
            "Confirm current state-level availability before relying on this listing."
        ),
        "phone": "181",
        "website": "https://www.india.gov.in/",
        "city": "India",
        "accessibility_notes": "Call availability and language options may vary by state.",
        "verified": False,
    },
    {
        "name": "Emergency Response Support",
        "category": "emergency",
        "description": (
            "For immediate danger, use the locally applicable emergency number. "
            "In India, 112 is the pan-India emergency response number; "
            "availability may depend on connectivity."
        ),
        "phone": "112",
        "website": "https://112.gov.in/",
        "city": "India",
        "accessibility_notes": (
            "If possible, move to a safer public location and ask a trusted person for help."
        ),
        "verified": False,
    },
    {
        "name": "One Stop Centre (find local centre)",
        "category": "legal-support",
        "description": (
            "One Stop Centres are intended to connect women affected by violence "
            "with multiple support services. Contact the relevant district authority "
            "to confirm the nearest centre and current services."
        ),
        "phone": None,
        "website": "https://www.india.gov.in/",
        "city": "India",
        "accessibility_notes": (
            "Confirm opening hours, accessibility, eligibility, and service availability "
            "before travelling."
        ),
        "verified": False,
    },
    {
        "name": "Counselling and Emotional Support",
        "category": "counselling",
        "description": (
            "Demo directory entry. "
            "Add a locally verified counselling provider before production use."
        ),
        "phone": None,
        "website": None,
        "city": "Nagpur",
        "accessibility_notes": "No provider has been verified for this demo entry.",
        "verified": False,
    },
    {
        "name": "Legal Aid Information (NALSA)",
        "category": "legal-support",
        "description": (
            "Demo directory entry. "
            "Confirm current district legal services authority contact details before use."
        ),
        "phone": None,
        "website": "https://nalsa.gov.in/",
        "city": "India",
        "accessibility_notes": "Contact the official provider to confirm eligibility and accessibility.",
        "verified": False,
    },
    {
        "name": "Shelter and Safe Housing Referral",
        "category": "shelter",
        "description": (
            "Demo directory entry for temporary safe-housing referral services. "
            "Replace with a locally verified shelter provider before production use."
        ),
        "phone": None,
        "website": None,
        "city": "Nagpur",
        "accessibility_notes": "No shelter has been verified for this demo entry.",
        "verified": False,
    },
    {
        "name": "iCall – Psychological Counselling",
        "category": "counselling",
        "description": (
            "iCall is a psycho-social helpline run by TISS that provides counselling "
            "services via phone, email and chat. "
            "Verify current availability and hours at icallhelpline.org."
        ),
        "phone": "9152987821",
        "website": "https://icallhelpline.org/",
        "city": "India",
        "accessibility_notes": (
            "Check the website for current language support, hours, and fee information."
        ),
        "verified": False,
    },
    {
        "name": "Childline India – Child Distress Helpline",
        "category": "helpline",
        "description": (
            "Childline 1098 is a 24/7 emergency response helpline for children in need. "
            "Confirm current local availability and service scope."
        ),
        "phone": "1098",
        "website": "https://www.childlineindia.org/",
        "city": "India",
        "accessibility_notes": "Service availability may vary by region. Verify before relying on this listing.",
        "verified": False,
    },
]


def seed_services(db: Session) -> None:
    """
    Insert demo service listings if the table is empty.

    This function is idempotent: it skips seeding if any record already exists.
    """
    if db.query(SupportService).count():
        return  # already seeded; do nothing

    for entry in DEMO_SERVICES:
        db.add(SupportService(**entry))
    db.commit()
