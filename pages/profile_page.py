from playwright.sync_api import Page
from pages.base_page import BasePage

class ProfilePage(BasePage):
    """Page Object for User Profile page (/profile) - US-18."""

    URL = f"{BasePage.BASE_URL}/profile"

    def __init__(self, page: Page):
        super().__init__(page)
        self.form = page.locator('form[data-test="profile_form"]')
        self.name_input = page.locator('input[data-test="profile_name_input"]')
        self.email_input = page.locator('input[data-test="profile_email_input"]')
        self.ico_input = page.locator('input[data-test="profile_ico_input"]')
        self.phone_input = page.locator('input[data-test="profile_phone_input"]')
        self.save_button = page.locator('form[data-test="profile_form"] button[data-test="registration_link"]:has-text("Uložit")')

    def open(self):
        """Navigate to profile page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        try:
            self.name_input.wait_for(state="visible", timeout=10000)
        except Exception:
            pass
        return self

    def update_profile(self, name: str = None, email: str = None, ico: str = None, phone: str = None):
        """Update profile fields and save."""
        if name is not None:
            self.name_input.fill(name)
        if email is not None:
            self.email_input.fill(email)
        if ico is not None:
            self.ico_input.fill(ico)
        if phone is not None:
            self.phone_input.fill(phone)
        self.save_button.click()
        try:
            self.page.wait_for_url("**/home*", timeout=5000)
        except Exception:
            self.page.wait_for_load_state("networkidle")

    def get_values(self) -> dict:
        """Return currently loaded input values in profile."""
        return {
            "name": self.name_input.input_value(),
            "email": self.email_input.input_value(),
            "ico": self.ico_input.input_value(),
            "phone": self.phone_input.input_value()
        }

