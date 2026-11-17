from playwright.sync_api import Page
from pages.base_page import BasePage

class PortalPage(BasePage):
    """Page Object for the root portal page (http://testovani.kitner.cz) - US-01."""

    URL = BasePage.BASE_URL

    def __init__(self, page: Page):
        super().__init__(page)
        self.kalkulacka_link = page.locator('a:has-text("Kalkulacka")')
        self.login_app_link = page.locator('a:has-text("Testovací login")')
        self.nextdate_link = page.locator('a:has-text("NextDate")')
        self.regkurz_link = page.locator('a:has-text("Registrace na kurz")')
        self.regkurz_vypis_link = page.locator('a:has-text("(výpis)")')
        self.demo_login_link = page.locator('a:has-text("Demo-login")')

    def open(self):
        """Navigate to root portal."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        return self
