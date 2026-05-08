class LoginPage:
    def __init__(self, page):
        self.page = page

        self.login_button = page.get_by_role("link", name="Log in")
        self.login_popup_headline = page.get_by_role("heading", name="Log in to your account")   
        self.username = page.locator("input[name=\"login\"]")
        self.password =  page.get_by_role("textbox", name="Password")
        self.submit_button = page.get_by_role("button", name="Log in")

    async def login(self, username, password):
        await self.username.fill(username)
        await self.password.fill(password)

 