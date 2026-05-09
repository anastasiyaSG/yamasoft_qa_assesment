import os
import logging
import playwright.async_api
import pytest_asyncio
from playwright.async_api import expect

from pages.login_page import LoginPage
from pages.my_trips_page import MyTripsPage
from pages.trip_creation_page import TripCreationPage
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


# for parralel execution test users should be handle from .env - TEST_USERS=[["user1@test.com","pass1"],["user2@test.com","pass2"]]
logger = logging.getLogger(__name__)

TIMEOUT = 10000

# ---------------------------------------------------------------------------
# Shared setup helpers
# ---------------------------------------------------------------------------
 
async def _dismiss_overlays(page) -> None:
    """
    Dismiss every known overlay that can block clicks on the page.
    All three are optional — their absence is not an error.
 
    Order matters: gist embed must go before the cookie banner because both
    can be present simultaneously, and the gist div sits on top.
    """
    # 1. Gist embed overlay — intercepts pointer events over the whole viewport
    try:
        gist_overlay = page.locator("#gist-overlay, #gist-embed-message")
        await expect(gist_overlay.first).to_be_visible(timeout=3000)
        await page.evaluate("""
            for (const id of ['gist-overlay', 'gist-embed-message']) {
                const el = document.getElementById(id);
                if (el) el.remove();
            }
        """)
        logger.debug("Gist embed overlay removed.")
    except Exception:
        logger.debug("Gist overlay not present.")
 
    # 2. Offer / marketing popup inside an iframe
    try:
        await (
            page.locator("iframe[title='Message']")
            .content_frame.get_by_role("button")
            .first.click(timeout=3000)
        )
        logger.debug("Offer popup dismissed.")
    except Exception:
        logger.debug("Offer popup not present.")
 
    # 3. Cookie consent banner
    try:
        await page.get_by_role("button", name="Accept All Cookies").click(timeout=3000)
        logger.debug("Cookie banner dismissed.")
    except Exception:
        logger.debug("Cookie banner not present.")
 
 
async def _start_trip(page, tcp: TripCreationPage) -> None:
    """Click Start Trip and wait for the destination form to appear."""
    await expect(tcp.start_trip).to_be_visible(timeout=TIMEOUT)
    await tcp.start_trip.click()
    await expect(tcp.where_are_you_going_heading).to_be_visible(timeout=TIMEOUT)
 
 
async def _fill_and_create_trip(tcp: TripCreationPage) -> None:
    """Fill trip details and submit the creation form."""
    await tcp.fill_trip_details()
    await tcp.create_trip_button.click()
 
 
async def _add_massachusetts_stop(page, tcp: TripCreationPage) -> None:
    """Add a Massachusetts stop on the trip page."""
    await expect(tcp.add_stops_input).to_be_visible(timeout=TIMEOUT)
    await page.get_by_role("textbox", name="Add stops").fill("m")
    await page.get_by_role("button", name="Massachusetts Massachusetts").click()
 
 
async def _safe_delete_trip(page) -> None:
    """Delete the current trip, swallowing errors so teardown never blocks."""
    try:
        await MyTripsPage(page).delete_trip()
    except Exception as exc:
        logger.warning("Trip cleanup failed (may already be deleted): %s", exc)
 
 
# ---------------------------------------------------------------------------
# Base browser fixture
# ---------------------------------------------------------------------------
 
@pytest_asyncio.fixture()
async def set_up_create_trip(request):
    """
    Open a browser tab, navigate to the app, and dismiss any overlays.
 
    The try/finally guarantees the browser always closes — even if page.goto()
    or _dismiss_overlays() raises during setup. Without it a failed setup
    leaks the browser process and leaves no trace or screenshot behind.
    """
    async with playwright.async_api.async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
 
        try:
            await page.goto(URL)
            logger.info("Navigated to %s", URL)
            await _dismiss_overlays(page)
 
            yield page
 
        finally:
            # Runs whether setup succeeded, the test failed, or setup itself raised.
            # Each step is individually guarded so one failure can't skip the rest.
            test_name = request.node.name
            try:
                await context.tracing.stop(path=f"traces/{test_name}.zip")
            except Exception as exc:
                logger.warning("Could not save trace for %s: %s", test_name, exc)
            try:
                await page.screenshot(path=f"traces/{test_name}.png")
            except Exception as exc:
                logger.warning("Could not save screenshot for %s: %s", test_name, exc)
            await context.close()
            await browser.close()
 
 
# ---------------------------------------------------------------------------
# Authenticated-session fixture
# ---------------------------------------------------------------------------
 
@pytest_asyncio.fixture()
async def login(set_up_create_trip):
    """Log in and ensure My Trips contains no leftover trips before yielding."""
    page = set_up_create_trip
    login_page = LoginPage(page)
 
    await expect(login_page.login_button).to_be_visible(timeout=TIMEOUT)
    # Re-run overlay dismissal: the gist embed can appear *after* initial load
    # and will silently block the login button for the full timeout.
    await _dismiss_overlays(page)
    await login_page.login_button.click()
    await expect(login_page.login_popup_headline).to_be_visible(timeout=TIMEOUT)
 
    await login_page.login(USERNAME, PASSWORD)
    await login_page.submit_button.click()
 
    await expect(page.get_by_role("button", name=USERNAME)).to_be_visible(timeout=TIMEOUT)
    logger.info("Login successful.")
 
    my_trips_page = MyTripsPage(page)
    await expect(my_trips_page.my_trips_button).to_be_visible(timeout=TIMEOUT)
    await my_trips_page.my_trips_button.click()
 
    # Remove any trip left over from a previous failed run
    try:
        await expect(my_trips_page.see_all_trips_button).not_to_be_visible(timeout=5000)
    except Exception:
        logger.warning("Stale trip found — running pre-test cleanup.")
        await _safe_delete_trip(page)
 
    yield page
    # Note: browser teardown is handled entirely by set_up_create_trip above.
    # No finally needed here — there is no resource opened in this fixture
    # that isn't already owned and closed by set_up_create_trip.
 
 
# ---------------------------------------------------------------------------
# Guest trip fixtures
# ---------------------------------------------------------------------------
 
@pytest_asyncio.fixture()
async def trip_no_registration(set_up_create_trip):
    """Guest: create a basic trip with no stops."""
    page = set_up_create_trip
    tcp = TripCreationPage(page)
    await _start_trip(page, tcp)
    await _fill_and_create_trip(tcp)
    yield page
    # No teardown needed: guest trips are not persisted to an account.
 
 
@pytest_asyncio.fixture()
async def trip_without_registration_with_stop(set_up_create_trip):
    """Guest: create a trip and add a Massachusetts stop."""
    page = set_up_create_trip
    tcp = TripCreationPage(page)
    await _start_trip(page, tcp)
    await _fill_and_create_trip(tcp)
    await _add_massachusetts_stop(page, tcp)
    yield page
    # No teardown needed: guest trips are not persisted to an account.
 
 
# ---------------------------------------------------------------------------
# Authenticated trip fixtures
# ---------------------------------------------------------------------------
 
@pytest_asyncio.fixture()
async def trip_with_registration(login):
    """
    Logged-in user: create a basic trip; delete it in teardown.
 
    The try/finally ensures _safe_delete_trip runs even when the test body
    itself raises — preventing trips accumulating across failed runs.
    """
    page = login
    tcp = TripCreationPage(page)
    await _start_trip(page, tcp)
    await _fill_and_create_trip(tcp)
    try:
        yield page
    finally:
        await _safe_delete_trip(page)
 
 
@pytest_asyncio.fixture()
async def trip_with_registration_with_stop(login):
    """
    Logged-in user: create a trip with a Massachusetts stop; delete it in teardown.
 
    The try/finally ensures _safe_delete_trip runs even when the test body
    itself raises — preventing trips accumulating across failed runs.
    """
    page = login
    tcp = TripCreationPage(page)
    await _start_trip(page, tcp)
    await _fill_and_create_trip(tcp)
    await _add_massachusetts_stop(page, tcp)
    try:
        yield page
    finally:
        await _safe_delete_trip(page)
 