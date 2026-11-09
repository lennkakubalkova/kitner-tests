from playwright.sync_api import Page
from pages.base_page import BasePage

class HomePage(BasePage):
    """Page Object for the Home dashboard page (/home)."""

    URL = f"{BasePage.BASE_URL}/home"

    def __init__(self, page: Page):
        super().__init__(page)
        self.welcome_heading = page.locator('h1, h2, h3, div:has-text("Vítej uživateli")')

    def open(self):
        """Navigate to home page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        return self

    def get_welcome_text(self) -> str:
        """Returns the welcome text if present."""
        if self.welcome_heading.first.is_visible():
            return self.welcome_heading.first.inner_text().strip()
        return ""

