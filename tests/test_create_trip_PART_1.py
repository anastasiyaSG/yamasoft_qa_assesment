import logging
import pytest
import playwright
from playwright.async_api import expect
from pages.my_trips_page import MyTripsPage
from pages.trip_creation_page import TripCreationPage
from utilities.helpers import safe_click

@pytest.mark.asyncio
@pytest.mark.smoke()
async def test_create_trip_no_registration(trip_no_registration):
    page = trip_no_registration
    creation_page = TripCreationPage(page)
    try:
        await expect(creation_page.launch_trip_button).to_be_visible()
    except:
        logging.error("Launch Trip button did not appear within the expected time.")
    try:
        await expect(page.get_by_role("heading", name="Do you have any places you")).to_be_visible()
    except:
        logging.error("Heading did not appear within the expected time.")
    try:
        await expect(page.get_by_text("Start planning your route. If")).to_be_visible()
    except:
        logging.error("Text did not appear within the expected time.")
    await creation_page.launch_trip_button.click()

    await expect(page.get_by_role("heading", name="Brooklyn Trip")).to_be_visible()

@pytest.mark.asyncio
@pytest.mark.smoke()    
async def test_create_trip_with_registration(trip_with_registration):
    page = trip_with_registration
    creation_page = TripCreationPage(page)
    try:
        await expect(creation_page.launch_trip_button).to_be_visible()
    except:
        logging.error("Launch Trip button did not appear within the expected time.")
    try:
        await expect(page.get_by_role("heading", name="Do you have any places you")).to_be_visible()
    except:
        logging.error("Heading did not appear within the expected time.")
    try:
        await expect(page.get_by_text("Start planning your route. If")).to_be_visible()
    except:
        logging.error("Text did not appear within the expected time.")
    await creation_page.launch_trip_button.click()
    try: 
        await expect(creation_page.explore_trip).to_be_visible(timeout=5000)
    except:
        logging.error("Explore trip button did not appear within the expected time.")
    await creation_page.explore_trip.click()
    await expect(page.get_by_role("heading", name="Brooklyn Trip")).to_be_visible()
    my_trips_page = MyTripsPage(page)
    try:
        await expect(my_trips_page.my_trips_button).to_be_visible()
    except:
        logging.error("My Trips button did not appear within the expected time.")
    await my_trips_page.my_trips_button.click()

    await expect(page.get_by_role("heading", name="Brooklyn Trip")).to_be_visible()
    await my_trips_page.delete_trip()

@pytest.mark.asyncio
@pytest.mark.smoke()
async def test_create_trip_with_registration_with_stops(trip_with_registration_with_stop):
    page = trip_with_registration_with_stop
    creation_page = TripCreationPage(page)
    try:
        await expect(creation_page.launch_trip_button).to_be_visible()
    except:
        logging.error("Launch Trip button did not appear within the expected time.")
    await creation_page.launch_trip_button.click()
    try: 
        await expect(creation_page.explore_trip).to_be_visible(timeout=5000)
    except:
        logging.error("Explore trip button did not appear within the expected time.")
    await creation_page.explore_trip.click()
    my_trips_page = MyTripsPage(page)
    try:
        await expect(my_trips_page.my_trips_button).to_be_visible()
    except:
        logging.error("My Trips button did not appear within the expected time.")
    await my_trips_page.my_trips_button.click()

    await expect(page.get_by_role("heading", name="Brooklyn Trip")).to_be_visible()
    await my_trips_page.delete_trip()


@pytest.mark.asyncio
async def test_create_trip_with_registration_without_destination(login):
    page = login
    creation_page = TripCreationPage(page)
    await creation_page.start_trip.click()
    try:
        await expect(creation_page.calendar_start_input).to_be_visible(timeout=5000)
    except:
        logging.error("Calendar did not open or create trip page did not load properly after clicking 'Start Trip'.")
    await creation_page.calendar_start_input.click()
    try:
        await expect(creation_page.calendar_day_10).to_be_visible(timeout=5000)
    except:
        logging.error("Calendar did not open or day 10 is not visible.")
    await creation_page.calendar_day_10.click()
    
    await creation_page.create_trip_button.click()
    await expect(creation_page.launch_trip_button).not_to_be_visible(timeout=5000)
   