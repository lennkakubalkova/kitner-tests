from playwright.sync_api import Page
from pages.base_page import BasePage

class RegisterPage(BasePage):
    """Page Object for the Registration page (/register) using robust data-test/data-testid attributes."""

    URL = f"{BasePage.BASE_URL}/register"

    def __init__(self, page: Page):
        super().__init__(page)
        self.form = page.locator('form[data-test="register_form"], form[data-testid="register_form"]')
        self.name_input = page.locator('input[data-test="name_input"], input[data-testid="name_input"]')
        self.email_input = page.locator('input[data-test="email_input"], input[data-testid="email_input"]')
        self.password_input = page.locator('input[data-test="password_input"], input[data-testid="password_input"]')
        self.password_confirmation_input = page.locator('input[data-test="password_again_input"], input[data-testid="password_again_input"]')
        self.submit_button = page.locator('button[data-test="register_button"], button[data-testid="register_button"]')
        self.heading = page.locator('div[data-test="register_text"], div[data-testid="register_text"]')
        self.login_link = page.locator('p[data-test="login_p"] a[data-test="login_link"], [data-testid="login_p"] [data-testid="login_link"]')

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
