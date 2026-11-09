from playwright.sync_api import Page
from pages.base_page import BasePage

class LoginPage(BasePage):
    """Page Object for the Login page (/login)."""

    URL = f"{BasePage.BASE_URL}/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = page.locator("#email_input")
        self.password_input = page.locator("#password_input")
        self.submit_button = page.locator('button[type="submit"]')
        self.heading = page.locator('h1, h2, h3, div:has-text("Přihlášení")').first
        self.register_link = page.locator('a[href="/register"]')
        self.forgot_password_link = page.locator('a[href="/forgot-password"]')

    def open(self):
        """Navigate directly to the login page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        return self

    def login(self, email: str, password: str):
        """Fill in credentials and submit the login form."""
        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()

        if password:
            self.password_input.fill(password)
        else:
            self.password_input.clear()

        self.submit_button.click()
        self.page.wait_for_timeout(1500)

