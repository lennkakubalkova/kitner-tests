from playwright.sync_api import Page
from pages.base_page import BasePage

class LoginPage(BasePage):
    """Page Object for the Login page (/login) using robust data-test/data-testid attributes."""

    URL = f"{BasePage.BASE_URL}/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.form = page.locator('form[data-test="login_form"], form[data-testid="login_form"]')
        self.email_input = page.locator('input[data-test="email_input"], input[data-testid="email_input"]')
        self.password_input = page.locator('input[data-test="password_input"], input[data-testid="password_input"]')
        self.submit_button = page.locator('button[data-test="login_button"], button[data-testid="login_button"]')
        self.heading = page.locator('div[data-test="login_text"], div[data-testid="login_text"]')
        self.register_link = page.locator('a[data-test="register_link"], a[data-testid="register_link"]')
        self.forgot_password_link = page.locator('a[data-test="forgot_password_link"], a[data-testid="forgot_password_link"]')

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
        if email and password:
            try:
                self.nav_logout.wait_for(state="visible", timeout=4000)
            except Exception:
                pass
        else:
            self.page.wait_for_timeout(1000)

    def click_forgot_password(self):
        """Click on 'Zapomněli jste heslo?' link."""
        self.forgot_password_link.click()
        self.page.wait_for_load_state("networkidle")

