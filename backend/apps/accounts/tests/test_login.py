"""
File:    backend/apps/accounts/tests/test_login.py
Purpose: End-to-end tests for the /api/v1/auth/ contract.
Owner:   Prashant

Login is the single most-used endpoint. A regression here cascades into every
dashboard, so these tests run on every PR and a failure blocks merge.

The tests exercise real HTTP + real DB + real JWT — no mocks, no shortcuts.
"""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient


LOGIN_URL = "/api/v1/auth/login/"
REFRESH_URL = "/api/v1/auth/refresh/"
LOGOUT_URL = "/api/v1/auth/logout/"
ME_URL = "/api/v1/auth/me/"


def _post_login(client: APIClient, email: str, password: str):
    return client.post(LOGIN_URL, {"email": email, "password": password}, format="json")


# ── Login ────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestLogin:
    def test_returns_user_and_access_in_body(self, api_client, principal_a, password):
        response = _post_login(api_client, principal_a.email, password)

        assert response.status_code == 200
        assert response.data["access"]
        assert "refresh" not in response.data, "refresh must never appear in body"

        user = response.data["user"]
        assert user["id"] == str(principal_a.id)
        assert user["email"] == principal_a.email
        assert user["role"] == "PRINCIPAL"
        assert user["school"] == str(principal_a.school_id)

    def test_sets_httponly_refresh_cookie(self, api_client, principal_a, password):
        response = _post_login(api_client, principal_a.email, password)
        cookie = response.cookies.get("refresh")

        assert cookie is not None, "refresh cookie must be set"
        assert cookie.value, "cookie value must not be empty"
        assert cookie["httponly"], "refresh cookie must be HttpOnly"
        assert cookie["samesite"].lower() == "lax"
        assert cookie["path"] == "/api/v1/auth/"
        assert int(cookie["max-age"]) == 7 * 24 * 60 * 60  # 7 days

    def test_wrong_password_returns_401(self, api_client, principal_a):
        response = _post_login(api_client, principal_a.email, "wrong-password")
        assert response.status_code == 401

    def test_unknown_email_returns_401(self, api_client, db):
        response = _post_login(api_client, "ghost@nowhere.test", "whatever")
        assert response.status_code == 401

    def test_inactive_user_is_rejected(self, api_client, principal_a, password):
        principal_a.is_active = False
        principal_a.save(update_fields=["is_active"])

        response = _post_login(api_client, principal_a.email, password)
        assert response.status_code == 401

    def test_email_match_is_case_insensitive(self, api_client, principal_a, password):
        response = _post_login(api_client, principal_a.email.upper(), password)
        assert response.status_code == 200

    def test_missing_email_is_400(self, api_client, db):
        response = api_client.post(LOGIN_URL, {"password": "x"}, format="json")
        assert response.status_code == 400

    def test_main_admin_has_null_school(self, api_client, main_admin, password):
        response = _post_login(api_client, main_admin.email, password)
        assert response.status_code == 200
        assert response.data["user"]["role"] == "MAIN_ADMIN"
        assert response.data["user"]["school"] is None


# ── Refresh ──────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestRefresh:
    def test_rotates_and_returns_new_access(self, api_client, principal_a, password):
        login = _post_login(api_client, principal_a.email, password)
        old_refresh = login.cookies["refresh"].value
        old_access = login.data["access"]

        response = api_client.post(REFRESH_URL)

        assert response.status_code == 200
        assert response.data["access"]
        assert response.data["access"] != old_access
        assert "refresh" not in response.data
        new_refresh = response.cookies["refresh"].value
        assert new_refresh and new_refresh != old_refresh, "refresh must rotate"

    def test_missing_cookie_returns_401(self, api_client, db):
        response = api_client.post(REFRESH_URL)
        assert response.status_code == 401
        assert response.data["code"] == "refresh_missing"

    def test_invalid_cookie_returns_401(self, api_client, db):
        api_client.cookies["refresh"] = "not-a-real-jwt"
        response = api_client.post(REFRESH_URL)
        assert response.status_code == 401

    def test_old_refresh_is_blacklisted_after_rotation(self, api_client, principal_a, password):
        _post_login(api_client, principal_a.email, password)
        old_refresh = api_client.cookies["refresh"].value

        first = api_client.post(REFRESH_URL)
        assert first.status_code == 200

        # Replay the old, now-blacklisted refresh token → must fail.
        api_client.cookies["refresh"] = old_refresh
        replay = api_client.post(REFRESH_URL)
        assert replay.status_code == 401


# ── Logout ───────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestLogout:
    def test_clears_cookie_and_blacklists_refresh(self, api_client, principal_a, password):
        _post_login(api_client, principal_a.email, password)
        refresh_before = api_client.cookies["refresh"].value

        response = api_client.post(LOGOUT_URL)

        assert response.status_code == 204
        cleared = response.cookies["refresh"]
        assert cleared.value == ""
        assert int(cleared["max-age"]) == 0

        # After logout the old refresh must not work any more.
        api_client.cookies["refresh"] = refresh_before
        replay = api_client.post(REFRESH_URL)
        assert replay.status_code == 401

    def test_logout_without_cookie_still_succeeds(self, api_client, db):
        response = api_client.post(LOGOUT_URL)
        assert response.status_code == 204


# ── /me/ ─────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestMe:
    def test_returns_current_user(self, api_client, principal_a, password, login):
        login(api_client, principal_a, password)

        response = api_client.get(ME_URL)
        assert response.status_code == 200
        assert response.data["id"] == str(principal_a.id)
        assert response.data["email"] == principal_a.email
        assert response.data["role"] == "PRINCIPAL"
        assert response.data["school"] == str(principal_a.school_id)

    def test_main_admin_school_is_null(self, api_client, main_admin, password, login):
        login(api_client, main_admin, password)

        response = api_client.get(ME_URL)
        assert response.status_code == 200
        assert response.data["role"] == "MAIN_ADMIN"
        assert response.data["school"] is None

    def test_requires_authentication(self, api_client, db):
        response = api_client.get(ME_URL)
        assert response.status_code == 401
