import pytest
import aiohttp

from actions.http_sessoion import BASE_URL, COMMON_HEADERS, LOGIN_URL, VALID_LOGIN, VALID_PASSWORD

@pytest.mark.skip(reason="API tests are not part of the current test suite")

class TestLoginSuccess:

    @pytest.mark.asyncio
    async def test_status_200(self, pre_auth_session):
        """Successful login returns HTTP 200."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN, "password": VALID_PASSWORD},
        ) as resp:
            assert resp.status == 200

    @pytest.mark.asyncio
    async def test_response_is_json(self, pre_auth_session):
        """Response Content-Type is application/json."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN, "password": VALID_PASSWORD},
        ) as resp:
            assert "application/json" in resp.headers.get("Content-Type", "")

    @pytest.mark.asyncio
    async def test_body_contains_auth_token(self, pre_auth_session):
        """Response body includes a non-empty auth_token string."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN, "password": VALID_PASSWORD},
        ) as resp:
            body = await resp.json(content_type=None)
            assert "auth_token" in body
            assert isinstance(body["auth_token"], str)
            assert len(body["auth_token"]) > 0

    @pytest.mark.asyncio
    async def test_body_contains_user_fields(self, pre_auth_session):
        """Response body includes expected user profile fields."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN, "password": VALID_PASSWORD},
        ) as resp:
            body = await resp.json(content_type=None)
            for field in ("id", "user_id", "username", "email", "admin", "avatar"):
                assert field in body, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_username_matches(self, pre_auth_session):
        """Returned username matches the login used."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN, "password": VALID_PASSWORD},
        ) as resp:
            body = await resp.json(content_type=None)
            assert body["username"] == VALID_LOGIN

    @pytest.mark.asyncio
    async def test_auth_token_cookie_is_set(self, pre_auth_session):
        """
        Server must set an auth_token cookie whose value matches the
        auth_token field in the JSON body.
        """
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN, "password": VALID_PASSWORD},
        ) as resp:
            body = await resp.json(content_type=None)
            cookies = {c.key: c.value for c in resp.cookies.values()}
            assert "auth_token" in cookies, "auth_token cookie was not set"
            assert cookies["auth_token"] == body["auth_token"]

    @pytest.mark.asyncio
    async def test_session_id_is_renewed_after_login(self, pre_auth_session):
        """
        The server must rotate _session_id on login to prevent
        session-fixation attacks.
        """
        old_cookies = {c.key: c.value for c in pre_auth_session.cookie_jar}
        old_session_id = old_cookies.get("_session_id")

        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN, "password": VALID_PASSWORD},
        ) as resp:
            new_cookies = {c.key: c.value for c in resp.cookies.values()}

        new_session_id = new_cookies.get("_session_id")
        assert new_session_id is not None
        assert new_session_id != old_session_id, (
            "_session_id was not rotated — potential session-fixation vulnerability."
        )


# ===========================================================================
# Negative / failure tests
# ===========================================================================
@pytest.mark.skip(reason="API tests are not part of the current test suite")

class TestLoginFailure:

    @pytest.mark.asyncio
    async def test_wrong_password_returns_4xx(self, pre_auth_session):
        """Wrong password must be rejected with a 4xx status."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN, "password": "wrong_password_123!"},
        ) as resp:
            assert resp.status in (401, 403, 422), (
                f"Expected 4xx for bad credentials, got {resp.status}"
            )

    @pytest.mark.asyncio
    async def test_wrong_password_no_auth_token_in_body(self, pre_auth_session):
        """Failed login must not include an auth_token in the response body."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN, "password": "wrong_password_123!"},
        ) as resp:
            if "application/json" in resp.headers.get("Content-Type", ""):
                body = await resp.json(content_type=None)
                assert not body.get("auth_token")

    @pytest.mark.asyncio
    async def test_missing_login_field(self, pre_auth_session):
        """Omitting the login field must be rejected."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"password": VALID_PASSWORD},
        ) as resp:
            assert resp.status in (400, 401, 422)

    @pytest.mark.asyncio
    async def test_missing_password_field(self, pre_auth_session):
        """Omitting the password field must be rejected."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": VALID_LOGIN},
        ) as resp:
            assert resp.status in (400, 401, 422)

    @pytest.mark.asyncio
    async def test_empty_credentials(self, pre_auth_session):
        """Empty strings for both fields must be rejected."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": "", "password": ""},
        ) as resp:
            assert resp.status in (400, 401, 422)

    @pytest.mark.asyncio
    async def test_nonexistent_user(self, pre_auth_session):
        """A login that does not exist must be rejected."""
        async with pre_auth_session.post(
            LOGIN_URL,
            json={"login": "totally_fake_user_xyz_99999", "password": "irrelevant"},
        ) as resp:
            assert resp.status in (401, 404, 422)


# ===========================================================================
# Token usage in follow-up requests
# ===========================================================================

@pytest.mark.skip(reason="API tests are not part of the current test suite")
class TestTokenUsage:

    @pytest.mark.asyncio
    async def test_auth_token_cookie_works_on_next_request(self, logged_in_session):
        session, _ = logged_in_session
        # NOTE: /users/me does not exist on this API — the real endpoint is:
        async with session.get(f"{BASE_URL}/api/web/current_user") as resp:
            assert resp.status not in (401, 403), (
                f"auth_token cookie was not accepted — got {resp.status}"
            )

    @pytest.mark.asyncio
    async def test_auth_token_as_bearer_header(self, logged_in_session):
        _, auth_token = logged_in_session
        headers = {**COMMON_HEADERS, "Authorization": f"Bearer {auth_token}"}
        async with aiohttp.ClientSession(headers=headers) as fresh_session:
            async with fresh_session.get(f"{BASE_URL}/api/web/current_user") as resp:
                assert resp.status not in (401, 403), (
                    f"Bearer token was not accepted — got {resp.status}"
                )