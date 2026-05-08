from playwright.async_api import expect


class MyTripsPage:
    """Page object for the My Trips page, providing methods to interact with trip listings and details."""
    
    def __init__(self, page):
        self.page = page
        self.my_trips_button = page.get_by_role("button", name="My trips")
        self.see_all_trips_button = page.get_by_role("link", name="See all trips")
        self.trip_details = page.locator(".list > section > .rt-menu > .rt-button")
        self.delete_trip_button = page.get_by_role("button", name="Delete Trip")
        self.delete_trip_pop_up =  page.get_by_role("button", name="Delete")

    async def delete_trip(self):
        await self.my_trips_button.click()
        await expect(self.see_all_trips_button).to_be_visible(timeout=5000)
        await self.see_all_trips_button.click()
        await self.trip_details.click()
        await self.delete_trip_button.click()
        await self.delete_trip_pop_up.click()