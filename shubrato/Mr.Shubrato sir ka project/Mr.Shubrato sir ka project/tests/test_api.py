"""
SAATHI API – smoke and privacy-contract tests.

These tests verify:
1. Health endpoint is reachable.
2. Service directory is seeded and all entries are marked unverified.
3. Services can be filtered by category.
4. Services can be searched by keyword.
5. Hazard report creation succeeds and the response never exposes coordinates.
6. Hazard report list endpoint returns reports and omits coordinates.
7. Support request requires consent=True (missing consent → 422).
8. Support request with consent=True returns a reference code and omits 'message'.
9. Service not found returns 404.
10. Hazard report description validation (too short → 422).
"""

import pytest


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body


# ---------------------------------------------------------------------------
# Service directory
# ---------------------------------------------------------------------------

def test_services_directory_is_seeded(client):
    """The directory must have at least one entry after startup."""
    response = client.get("/api/v1/services")
    assert response.status_code == 200
    services = response.json()
    assert isinstance(services, list)
    assert len(services) > 0


def test_all_seed_entries_are_unverified(client):
    """Every seed entry must have verified=False (demo data disclaimer)."""
    response = client.get("/api/v1/services")
    services = response.json()
    assert all(s["verified"] is False for s in services), (
        "All seed entries should be unverified demo listings."
    )


def test_services_filter_by_category(client):
    """Category filter must return only matching entries."""
    response = client.get("/api/v1/services", params={"category": "helpline"})
    assert response.status_code == 200
    services = response.json()
    assert all(s["category"] == "helpline" for s in services)


def test_services_search_by_keyword(client):
    """Keyword search must return entries that match."""
    response = client.get("/api/v1/services", params={"q": "emergency"})
    assert response.status_code == 200
    services = response.json()
    # There should be at least the emergency seed entry.
    assert any("emergency" in s["description"].lower() or s["category"] == "emergency"
               for s in services)


def test_service_by_id_found(client):
    """GET /services/{id} must return a single service entry."""
    # Retrieve the list to get a valid id.
    list_resp = client.get("/api/v1/services")
    first_id = list_resp.json()[0]["id"]

    response = client.get(f"/api/v1/services/{first_id}")
    assert response.status_code == 200
    assert response.json()["id"] == first_id


def test_service_by_id_not_found(client):
    """GET /services/{id} must return 404 for a non-existent id."""
    response = client.get("/api/v1/services/999999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Hazard reports
# ---------------------------------------------------------------------------

def test_hazard_report_creation_succeeds(client):
    """A valid hazard payload must create a report and return 201."""
    payload = {
        "category": "streetlight",
        "description": "Streetlight is not working beside the public footpath.",
        "location_text": "Near the community bus stop",
        "latitude": 21.1458,
        "longitude": 79.0882,
    }
    response = client.post("/api/v1/hazards", json=payload)
    assert response.status_code == 201
    result = response.json()
    assert result["reference_code"].startswith("SAF-")
    assert result["status"] == "received"


def test_hazard_report_does_not_expose_coordinates(client):
    """Latitude and longitude must NEVER appear in any hazard API response."""
    payload = {
        "category": "streetlight",
        "description": "Streetlight is not working beside the public footpath.",
        "location_text": "Near the community bus stop",
        "latitude": 21.1458,
        "longitude": 79.0882,
    }
    response = client.post("/api/v1/hazards", json=payload)
    assert response.status_code == 201
    result = response.json()
    assert "latitude"  not in result, "latitude must not be in the hazard response"
    assert "longitude" not in result, "longitude must not be in the hazard response"


def test_hazard_list_also_omits_coordinates(client):
    """The list endpoint must also omit coordinates for every entry."""
    response = client.get("/api/v1/hazards")
    assert response.status_code == 200
    for report in response.json():
        assert "latitude"  not in report
        assert "longitude" not in report


def test_hazard_report_description_too_short(client):
    """Description shorter than 5 characters must be rejected with 422."""
    payload = {
        "category": "streetlight",
        "description": "Bad",          # too short (min=5)
        "location_text": "Bus stop",
    }
    response = client.post("/api/v1/hazards", json=payload)
    assert response.status_code == 422


def test_hazard_category_required(client):
    """Missing category must be rejected with 422."""
    payload = {
        "description": "Streetlight broken.",
        "location_text": "Main road",
    }
    response = client.post("/api/v1/hazards", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Support requests (privacy contract)
# ---------------------------------------------------------------------------

def test_support_request_requires_consent(client):
    """Submitting without consent must be rejected (422)."""
    payload = {
        "support_type": "counselling",
        "preferred_contact": "self-directed",
        "message": "I want information about support options.",
        # consent is absent → 422
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 422


def test_support_request_false_consent_rejected(client):
    """Submitting with consent=false must also be rejected."""
    payload = {
        "support_type": "counselling",
        "preferred_contact": "self-directed",
        "message": "I want information about support options.",
        "consent": False,
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 422


def test_support_request_returns_reference_without_contacting_provider(client):
    """A valid submission must return a reference code with status 'received'."""
    payload = {
        "support_type": "counselling",
        "preferred_contact": "self-directed",
        "message": "Please show me information about available options.",
        "consent": True,
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 201
    result = response.json()
    assert result["reference_code"].startswith("SUP-")
    assert result["status"] == "received"


def test_support_request_does_not_echo_message(client):
    """The 'message' field must NOT appear in the support-request response."""
    payload = {
        "support_type": "counselling",
        "preferred_contact": "self-directed",
        "message": "Sensitive personal narrative.",
        "consent": True,
    }
    response = client.post("/api/v1/support-requests", json=payload)
    assert response.status_code == 201
    result = response.json()
    assert "message" not in result, (
        "'message' must not be returned in the support-request response "
        "to prevent accidental exposure of sensitive narratives."
    )


def test_support_request_reference_codes_are_unique(client):
    """Each submission must generate a distinct reference code."""
    payload = {
        "support_type": "legal-support",
        "preferred_contact": "self-directed",
        "consent": True,
    }
    r1 = client.post("/api/v1/support-requests", json=payload).json()
    r2 = client.post("/api/v1/support-requests", json=payload).json()
    assert r1["reference_code"] != r2["reference_code"]


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------

def test_root_endpoint(client):
    """The root / endpoint must confirm the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
