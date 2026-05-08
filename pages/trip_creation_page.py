import logging

from playwright.async_api import Page, expect

class TripCreationPage:

    
    def __init__(self, page: Page):
        self.page = page
        self.start_trip = page.get_by_role("button", name="Start Trip")
        self.where_are_you_going_heading = page.get_by_role("heading", name="Where are you going?")
        self.starting_point_input = page.get_by_role("textbox", name="Starting point")
        self.destination_input = page.get_by_role("textbox", name="Destination")
        self.create_trip_button = page.get_by_role("button", name="Create trip")
        self.launch_trip_button = page.get_by_role("button", name="Launch trip")
        self.calendar_start_input = page.get_by_role("textbox", name="Start", exact=True)
        self.calendar_day_10 = page.get_by_role("gridcell", name="10")
        self.create_trip_button = page.get_by_role("button", name="Create trip")
        self.add_stops_input = page.get_by_role("textbox", name="Add stops")
        self.launch_trip_button = page.get_by_role("button", name="Launch trip")
        self.close_trip = page.get_by_role("button", name="Close trip")
        self.explore_trip = page.get_by_role("button", name="Start exploring")

    async def fill_trip_details(self):
        await self.starting_point_input.fill('A')
        try:
            await expect(self.starting_point_input).to_have_value('A', timeout=5000)
            logging.info("Starting point input filled successfully.")
        except:
            logging.error("Failed to fill starting point input.")
        try:
            await expect(self.page.get_by_role("button", name="Arizona Arizona United States")).to_be_visible(timeout=5000)
            await self.page.get_by_role("button", name="Arizona Arizona United States").click()
            logging.info("Starting point suggestion selected successfully.")
        except:
            logging.error("Failed to select starting point suggestion.")
        try:
            await self.destination_input.fill('B')
            logging.info("Destination input filled successfully.")
        except:
            logging.error("Failed to fill destination input.")
        try:
            await expect(self.page.get_by_role("button", name="Brooklyn Brooklyn NY, United")).to_be_visible(timeout=5000)
            await self.page.get_by_role("button", name="Brooklyn Brooklyn NY, United").click()
            logging.info("Destination suggestion selected successfully.")
        except:
            logging.error("Failed to select destination suggestion.")
        try:
            await self.calendar_start_input.click()
            await expect(self.calendar_day_10).to_be_visible(timeout=5000)
        except:
            logging.error("Calendar did not open or day 10 is not visible.")
        await self.calendar_day_10.click()
        
