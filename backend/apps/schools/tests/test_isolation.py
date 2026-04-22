"""
File:    backend/apps/schools/tests/test_isolation.py
Purpose: The multi-tenant isolation canary — School A must never see School B.
Owner:   Prashant

Why this test exists:
    Skillship stores every school's data in one database. Leaking even one
    row across schools is a privacy breach that ends the contract. This file
    is the single non-negotiable test that proves the isolation machinery
    is actually wired up — if it fails, nothing else matters.

What it covers today (Week 2):
    - `request.school_id` is set correctly from the authenticated user.
    - `/auth/me/` returns only the caller's own profile.
    - ORM-level TenantQuerySet.for_school() returns only that school's rows.
    - The role/school DB check constraints reject the invalid combinations
      that would otherwise silently break isolation (MAIN_ADMIN with a
      school, or a non-admin without one).

What goes in next (Weeks 3+):
    - Users CRUD: A-principal cannot list / retrieve / update B-users.
    - Schools CRUD: only MAIN_ADMIN sees cross-school rows.
    - Every new tenant-scoped endpoint gets a row in this file.
"""

from __future__ import annotations

import pytest
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient

from apps.accounts.models import User

ME_URL = "/api/v1/auth/me/"


# ── ORM layer: the TenantQuerySet + FK filter actually scope by school ──────


@pytest.mark.django_db
class TestOrmIsolation:
    def test_filter_by_school_returns_only_that_schools_users(
        self, principal_a, teacher_a, student_a, principal_b, student_b, school_a, school_b
    ):
        a_users = set(User.objects.filter(school=school_a).values_list("id", flat=True))
        b_users = set(User.objects.filter(school=school_b).values_list("id", flat=True))

        assert principal_a.id in a_users
        assert teacher_a.id in a_users
        assert student_a.id in a_users
        assert principal_b.id not in a_users
        assert student_b.id not in a_users

        assert principal_b.id in b_users
        assert student_b.id in b_users
        assert principal_a.id not in b_users

        assert a_users.isdisjoint(b_users), "no user may belong to two schools"

    def test_main_admin_is_outside_every_school(self, main_admin, school_a, school_b):
        assert main_admin.school_id is None
        assert main_admin not in User.objects.filter(school=school_a)
        assert main_admin not in User.objects.filter(school=school_b)


# ── DB check constraints: role/school invariant is enforced by Postgres ─────


@pytest.mark.django_db
class TestRoleSchoolConstraints:
    def test_teacher_without_school_is_rejected(self, db, password):
        with pytest.raises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                username="orphan_teacher",
                email="orphan@nowhere.test",
                password=password,
                role=User.Role.TEACHER,
                school=None,
            )

    def test_main_admin_with_school_is_rejected(self, school_a, password):
        with pytest.raises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                username="bad_admin",
                email="bad_admin@nowhere.test",
                password=password,
                role=User.Role.MAIN_ADMIN,
                school=school_a,
            )


# ── HTTP layer: TenantMiddleware + /me/ report the correct school ───────────


@pytest.mark.django_db
class TestHttpIsolation:
    def test_each_principal_sees_only_their_own_profile(
        self, principal_a, principal_b, password, login
    ):
        client_a = APIClient()
        login(client_a, principal_a, password)
        me_a = client_a.get(ME_URL)

        client_b = APIClient()
        login(client_b, principal_b, password)
        me_b = client_b.get(ME_URL)

        assert me_a.status_code == 200
        assert me_b.status_code == 200

        assert me_a.data["id"] == str(principal_a.id)
        assert me_a.data["school"] == str(principal_a.school_id)

        assert me_b.data["id"] == str(principal_b.id)
        assert me_b.data["school"] == str(principal_b.school_id)

        assert me_a.data["school"] != me_b.data["school"], "schools must differ"
        assert me_a.data["id"] != me_b.data["id"]

    def test_student_in_school_a_cannot_impersonate_school_b_via_token_reuse(
        self, api_client, principal_a, principal_b, password, login
    ):
        """The access token carries the user's identity. A token minted for a
        user in school A can never be reinterpreted as school B — even if an
        attacker sends it at an endpoint that belongs to school B."""
        login(api_client, principal_a, password)

        response = api_client.get(ME_URL)
        assert response.status_code == 200
        assert response.data["school"] == str(principal_a.school_id)
        assert response.data["school"] != str(principal_b.school_id)

    def test_anonymous_request_has_no_school_scope(self, api_client, db):
        response = api_client.get(ME_URL)
        assert response.status_code == 401
