"""
File:    backend/conftest.py
Purpose: Shared pytest fixtures — tenant-aware users, schools, and helpers.
Owner:   Navanish

Every test that hits an endpoint requiring auth should use `login(client, user)`
to populate the Authorization header and the refresh cookie. This keeps the
login flow itself exercised on every test (no shortcut fixtures that bypass
the real JWT issuance — we want to catch regressions there).
"""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.schools.models import School

DEFAULT_PASSWORD = "Skillship#Test-2026"


# ── Clients ──────────────────────────────────────────────────────────────────


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def password() -> str:
    return DEFAULT_PASSWORD


# ── Tenants ──────────────────────────────────────────────────────────────────


@pytest.fixture
def school_a(db) -> School:
    return School.objects.create(
        name="Delhi Public School — A",
        slug="dps-a",
        board=School.Board.CBSE,
        city="Delhi",
        state="Delhi",
    )


@pytest.fixture
def school_b(db) -> School:
    return School.objects.create(
        name="St. Xavier's — B",
        slug="sxb-b",
        board=School.Board.ICSE,
        city="Mumbai",
        state="Maharashtra",
    )


# ── Users ────────────────────────────────────────────────────────────────────


def _make_user(*, username: str, email: str, role: str, school: School | None, password: str) -> User:
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=username.split("_")[0].title(),
        last_name=(school.slug if school else "Platform").title(),
        role=role,
        school=school,
    )


@pytest.fixture
def main_admin(db, password) -> User:
    return _make_user(
        username="main_admin",
        email="admin@skillship.test",
        role=User.Role.MAIN_ADMIN,
        school=None,
        password=password,
    )


@pytest.fixture
def principal_a(school_a, password) -> User:
    return _make_user(
        username="principal_a",
        email="principal@dps-a.test",
        role=User.Role.PRINCIPAL,
        school=school_a,
        password=password,
    )


@pytest.fixture
def teacher_a(school_a, password) -> User:
    return _make_user(
        username="teacher_a",
        email="teacher@dps-a.test",
        role=User.Role.TEACHER,
        school=school_a,
        password=password,
    )


@pytest.fixture
def student_a(school_a, password) -> User:
    return _make_user(
        username="student_a",
        email="student@dps-a.test",
        role=User.Role.STUDENT,
        school=school_a,
        password=password,
    )


@pytest.fixture
def principal_b(school_b, password) -> User:
    return _make_user(
        username="principal_b",
        email="principal@sxb-b.test",
        role=User.Role.PRINCIPAL,
        school=school_b,
        password=password,
    )


@pytest.fixture
def student_b(school_b, password) -> User:
    return _make_user(
        username="student_b",
        email="student@sxb-b.test",
        role=User.Role.STUDENT,
        school=school_b,
        password=password,
    )


# ── Auth helper ──────────────────────────────────────────────────────────────


@pytest.fixture
def login():
    """Log a user in through the real endpoint and attach Bearer + refresh cookie.

    Using the real endpoint keeps every test honest about the login contract —
    a regression in LoginView breaks every downstream test, which is what we want.
    """

    def _login(client: APIClient, user: User, password: str = DEFAULT_PASSWORD):
        response = client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": password},
            format="json",
        )
        assert response.status_code == 200, response.content
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response

    return _login
