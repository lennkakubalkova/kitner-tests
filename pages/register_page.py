from playwright.sync_api import Page
from pages.base_page import BasePage

class RegisterPage(BasePage):
    """Page Object for the Registration page (/register)."""

    URL = f"{BasePage.BASE_URL}/register"

    def __init__(self, page: Page):
        super().__init__(page)
        self.name_input = page.locator('input[placeholder="Jméno"]')
        self.email_input = page.locator('input[placeholder="Email"]')
        self.password_input = page.locator('input[placeholder="Heslo"]')
        self.password_confirmation_input = page.locator('input[placeholder="Heslo znovu"]')
        self.submit_button = page.locator('button[type="submit"]')
        self.login_link = page.locator('a:has-text("Přihlašte se zde."), a:has-text("Přihlaste se zde.")')

    def open(self):
        """Navigate to the register page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        return self

    def register(self, name: str = "", email: str = "", password: str = "", password_confirmation: str = ""):
        """Fill registration fields and click submit button."""
        if name:
            self.name_input.fill(name)
        else:
            self.name_input.clear()

        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()

        if password:
            self.password_input.fill(password)
        else:
            self.password_input.clear()

        if password_confirmation:
            self.password_confirmation_input.fill(password_confirmation)
        else:
            self.password_confirmation_input.clear()

        self.submit_button.click()
        self.page.wait_for_timeout(1500)
