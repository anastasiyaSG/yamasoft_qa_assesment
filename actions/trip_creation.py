import os
import playwright.async_api
from pathlib import Path
import pytest_asyncio
import logging
from playwright.async_api import expect
from pages import trip_creation_page
from pages.my_trips_page import MyTripsPage
from pages.trip_creation_page import TripCreationPage
from utilities.helpers import safe_click, wait_for_toasts_to_disapper

from pages.login_page import LoginPage
from dotenv import load_dotenv

load_dotenv()
URL= os.getenv("BASE_URL")

#to do enhance different browser support and parallel execution with pytest-xdist
@pytest_asyncio.fixture()
async def set_up_create_trip(request):
    async with playwright.async_api.async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)

        await page.goto(URL)
        logging.info(f"Navigated to {URL}")
        try:
            await page.locator("iframe[title=\"Message\"]").content_frame.get_by_role("button").first.click()
        except:
            logging.warning("Failed to click the offer popup.")
        try:
            await page.get_by_role("button", name="Accept All Cookies").click()
        except:
            logging.warning("Failed to click the cookie consent button.")

        yield page
        
        test_name = request.node.name
        screenshot_path = f"traces/{test_name}.png"
        await context.tracing.stop(path=f"traces/{test_name}.zip")
        await page.screenshot(path=screenshot_path)

        
        await context.close()
        await browser.close()

@pytest_asyncio.fixture()
async def login(set_up_create_trip):
    page = set_up_create_trip
    login_page = LoginPage(page)
    await expect(login_page.login_button).to_be_visible(timeout=5000)
    await login_page.login_button.click()
    try:
        await expect(login_page.login_popup_headline).to_be_visible(timeout=5000)
    except:
        logging.error("Login popup did not appear within the expected time.")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    await login_page.login(username, password)
    await login_page.submit_button.click()
    try:
        await expect(page.get_by_role("button", name=username)).to_be_visible(timeout=5000)
        logging.info("Login successful, user recognized.")
    except:
        logging.error("Login failed or user not recognized.")
    my_trips_page = MyTripsPage(page)
    try:
        await expect(my_trips_page.my_trips_button).to_be_visible(timeout=5000)
        logging.info("My Trips button is visible after login.")
    except:
        logging.error("My Trips button did not appear within the expected time.")
    try: 
        await my_trips_page.my_trips_button.click()
        await expect(my_trips_page.see_all_trips_button).not_to_be_visible(timeout=5000)
    except:
        logging.warning("Old trips are still visible after login, cleanup might have failed.")
        await my_trips_page.delete_trip()
    
    yield page

@pytest_asyncio.fixture()
async def trip_no_registration(set_up_create_trip):
    page = set_up_create_trip
    trip_creation_page = TripCreationPage(page)
    try:
        await expect(trip_creation_page.start_trip).to_be_visible(timeout=5000)
    except:
        logging.error("Start Trip button did not appear within the expected time.")
    await trip_creation_page.start_trip.click()
    try:
        await expect(trip_creation_page.where_are_you_going_heading).to_be_visible(timeout=5000)
    except:
        logging.error("Trip creation page did not load properly after clicking 'Start Trip'.")
    await trip_creation_page.fill_trip_details()
    await trip_creation_page.create_trip_button.click()

    yield page

@pytest_asyncio.fixture()
async def trip_with_registration(login):
    page = login
    trip_creation_page = TripCreationPage(page)
    try:
        await expect(trip_creation_page.start_trip).to_be_visible(timeout=5000)
    except:
        logging.error("Start Trip button did not appear within the expected time.")
    await trip_creation_page.start_trip.click()
    try:
        await expect(trip_creation_page.where_are_you_going_heading).to_be_visible(timeout=5000)
    except:
        logging.error("Trip creation page did not load properly after clicking 'Start Trip'.")
    await trip_creation_page.fill_trip_details()
    await trip_creation_page.create_trip_button.click()

    my_trips_page = MyTripsPage(page)
    try:
        await my_trips_page.delete_trip()
    except Exception as e:
        logging.warning(f"Cleanup failed: {e}")


    yield page

@pytest_asyncio.fixture()
async def trip_with_registration_with_stop(login):
    page = login
    trip_creation_page = TripCreationPage(page)
    try:
        await expect(trip_creation_page.start_trip).to_be_visible(timeout=5000)
    except:
        logging.error("Start Trip button did not appear within the expected time.")
    await trip_creation_page.start_trip.click()
    try:
        await expect(trip_creation_page.where_are_you_going_heading).to_be_visible(timeout=5000)
    except:
        logging.error("Trip creation page did not load properly after clicking 'Start Trip'.")
    await trip_creation_page.fill_trip_details()
    await trip_creation_page.create_trip_button.click()
    try:
        await expect(trip_creation_page.add_stops_input).to_be_visible(timeout=5000)
    except:
        logging.error("Add stops input did not appear within the expected time.")
    try:
        await page.get_by_role("textbox", name="Add stops").fill("m")
    except:
        logging.error("Failed to fill add stops input.")
    try:
        await page.get_by_role("button", name="Massachusetts Massachusetts").click()
    except:
        logging.error("Failed to click Massachusetts suggestion.")

    my_trips_page = MyTripsPage(page)
    try:
        await my_trips_page.delete_trip()
    except Exception as e:
        logging.warning(f"Cleanup failed: {e}")
    yield page

@pytest_asyncio.fixture()
async def trip_without_registration_with_stop(set_up_create_trip):
    page = set_up_create_trip
    trip_creation_page = TripCreationPage(page)
    try:
        await expect(trip_creation_page.start_trip).to_be_visible(timeout=5000)
    except:
        logging.error("Start Trip button did not appear within the expected time.")
    await trip_creation_page.start_trip.click()
    try:
        await expect(trip_creation_page.where_are_you_going_heading).to_be_visible(timeout=5000)
    except:
        logging.error("Trip creation page did not load properly after clicking 'Start Trip'.")
    await trip_creation_page.fill_trip_details()
    await trip_creation_page.create_trip_button.click()
    try:
        await expect(trip_creation_page.add_stops_input).to_be_visible(timeout=5000)
    except:
        logging.error("Add stops input did not appear within the expected time.")
    try:
        await page.get_by_role("textbox", name="Add stops").fill("m")
    except:
        logging.error("Failed to fill add stops input.")
    try:
        await page.get_by_role("button", name="Massachusetts Massachusetts").click()
    except:
        logging.error("Failed to click Massachusetts suggestion.")
    yield page



