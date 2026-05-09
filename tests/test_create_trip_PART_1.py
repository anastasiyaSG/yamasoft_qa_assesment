import logging
import pytest
from playwright.async_api import expect

from pages.my_trips_page import MyTripsPage
from pages.trip_creation_page import TripCreationPage

logger = logging.getLogger(__name__)

TIMEOUT = 7000
BROOKLYN_TRIP_HEADING = "Brooklyn Trip"
PLACES_HEADING = "Do you have any places you"
PLANNING_TEXT = "Start planning your route. If"


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.smoke
async def test_create_trip_no_registration(trip_no_registration):
    """
    Guest creates a trip and launches it.
    Asserts the post-launch trip heading is visible.
    """
    page = trip_no_registration
    creation_page = TripCreationPage(page)

    await expect(creation_page.launch_trip_button).to_be_visible(timeout=TIMEOUT)
    await expect(page.get_by_role("heading", name=PLACES_HEADING)).to_be_visible(timeout=TIMEOUT)
    await expect(page.get_by_text(PLANNING_TEXT)).to_be_visible(timeout=TIMEOUT)

    await creation_page.launch_trip_button.click()

    await expect(
        page.get_by_role("heading", name=BROOKLYN_TRIP_HEADING)
    ).to_be_visible(timeout=TIMEOUT)


@pytest.mark.asyncio
@pytest.mark.smoke
async def test_create_trip_with_registration(trip_with_registration):
    """
    Logged-in user creates a trip, launches it, navigates to My Trips,
    and confirms the trip persists. Deletes the trip at the end.
    """
    page = trip_with_registration
    creation_page = TripCreationPage(page)
    my_trips_page = MyTripsPage(page)

    await expect(creation_page.launch_trip_button).to_be_visible(timeout=TIMEOUT)
    await expect(page.get_by_role("heading", name=PLACES_HEADING)).to_be_visible(timeout=TIMEOUT)
    await expect(page.get_by_text(PLANNING_TEXT)).to_be_visible(timeout=TIMEOUT)

    await creation_page.launch_trip_button.click()
    await expect(creation_page.explore_trip).to_be_visible(timeout=TIMEOUT)
    await creation_page.explore_trip.click()

    await expect(
        page.get_by_role("heading", name=BROOKLYN_TRIP_HEADING)
    ).to_be_visible(timeout=TIMEOUT)

    await expect(my_trips_page.my_trips_button).to_be_visible(timeout=TIMEOUT)
    await my_trips_page.my_trips_button.click()

    await expect(
        page.get_by_role("heading", name=BROOKLYN_TRIP_HEADING)
    ).to_be_visible(timeout=TIMEOUT)

    await my_trips_page.delete_trip()


@pytest.mark.asyncio
@pytest.mark.smoke
async def test_create_trip_with_registration_with_stops(trip_with_registration_with_stop):
    """
    Logged-in user creates a trip with a Massachusetts stop, launches it,
    and confirms the trip appears in My Trips. Deletes the trip at the end.
    """
    page = trip_with_registration_with_stop
    creation_page = TripCreationPage(page)
    my_trips_page = MyTripsPage(page)

    await expect(creation_page.launch_trip_button).to_be_visible(timeout=TIMEOUT)
    await creation_page.launch_trip_button.click()

    await expect(creation_page.explore_trip).to_be_visible(timeout=TIMEOUT)
    await creation_page.explore_trip.click()

    await expect(my_trips_page.my_trips_button).to_be_visible(timeout=TIMEOUT)
    await my_trips_page.my_trips_button.click()

    await expect(
        page.get_by_role("heading", name=BROOKLYN_TRIP_HEADING)
    ).to_be_visible(timeout=TIMEOUT)

    await my_trips_page.delete_trip()


# ---------------------------------------------------------------------------
# Validation / edge-case tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_trip_with_registration_without_destination(login):
    """
    Logged-in user opens trip creation, selects only a date (no destination),
    and submits. Asserts the Launch Trip button does NOT appear,
    confirming the form blocks incomplete submissions.
    """
    page = login
    creation_page = TripCreationPage(page)

    await creation_page.start_trip.click()

    await expect(creation_page.calendar_start_input).to_be_visible(timeout=TIMEOUT)
    await creation_page.calendar_start_input.click()

    await expect(creation_page.calendar_day_10).to_be_visible(timeout=TIMEOUT)
    await creation_page.calendar_day_10.click()

    await creation_page.create_trip_button.click()

    await expect(creation_page.launch_trip_button).not_to_be_visible(timeout=TIMEOUT)