import os
import aiohttp
import pytest
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from yarl import URL
load_dotenv()

BASE_URL       = os.getenv("BASE_URL", "https://maps.roadtrippers.com").rstrip("/")
LOGIN_URL      = f"{BASE_URL}/user_sessions"
VALID_LOGIN    = os.getenv("USERNAME")
VALID_PASSWORD = os.getenv("PASSWORD")
RECAPTCHA_SITE_KEY = "6Ldsz4wrAAAAAGTSgTB9UhLyTKAVIkSLdJS_RWCn"

COMMON_HEADERS = {
    "Content-Type":   "application/json",
    "Accept":         "*/*",
    "User-Agent":     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/147.0.0.0 Safari/537.36",
    "Referer":        f"{BASE_URL}/?lng=-98.35&lat=39.5&z=3.30945",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9",
}




def _get_session_id(cookie_jar, base_url: str) -> str | None:
    cookies = cookie_jar.filter_cookies(URL(base_url))
    cookie = cookies.get("_session_id")
    return cookie.value if cookie else None


async def _get_recaptcha_token_via_browser() -> tuple[str, str]:
    """
    Opens a real Chromium browser, loads the Roadtrippers homepage,
    executes grecaptcha.execute() and returns (recaptcha_token, session_id).
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(f"{BASE_URL}/?lng=-98.35&lat=39.5&z=3.30945",
                         wait_until="domcontentloaded", timeout=60000)

        # Wait for grecaptcha to be available on the page
        await page.wait_for_function("typeof grecaptcha !== 'undefined'", timeout=30000)

        token = await page.evaluate(f"""
            () => new Promise((resolve, reject) => {{
                grecaptcha.ready(() => {{
                    grecaptcha.execute('{RECAPTCHA_SITE_KEY}', {{action: 'login'}})
                        .then(resolve)
                        .catch(reject);
                }});
            }})
        """)

        # Extract _session_id cookie set by the browser
        cookies = await context.cookies(BASE_URL)
        session_id = next(
            (c["value"] for c in cookies if c["name"] == "_session_id"), None
        )

        await browser.close()
        return token, session_id


@pytest.fixture()
async def http_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture()
async def pre_auth_session():
    async with aiohttp.ClientSession(headers=COMMON_HEADERS) as session:
        resp = await session.get(BASE_URL)
        await resp.read()
        session_id = _get_session_id(session.cookie_jar, BASE_URL)
        assert session_id is not None, (
            f"_session_id not set. Cookies: {dict(session.cookie_jar._cookies)}"
        )
        yield session


@pytest.fixture()
async def logged_in_session():
    """
    Uses a real browser to get a valid reCAPTCHA token + session cookie,
    then completes login via aiohttp and yields (session, auth_token).
    """
    recaptcha_token, session_id = await _get_recaptcha_token_via_browser()

    jar = aiohttp.CookieJar()
    async with aiohttp.ClientSession(headers=COMMON_HEADERS, cookie_jar=jar) as session:
        # Seed the session cookie the browser obtained
        session.cookie_jar.update_cookies(
            {"_session_id": session_id},
            response_url=aiohttp.client_reqrep.URL(BASE_URL),
        )

        async with session.post(
            LOGIN_URL,
            json={
                "login": VALID_LOGIN,
                "password": VALID_PASSWORD,
                "recaptcha": {
                    "site_key": RECAPTCHA_SITE_KEY,
                    "token": recaptcha_token,
                },
            },
        ) as resp:
            assert resp.status == 200, (
                f"Login failed: {resp.status} — recaptcha token may have expired"
            )
            body = await resp.json(content_type=None)
            auth_token = body["auth_token"]

        yield session, auth_token