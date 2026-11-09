from playwright.sync_api import Page
from pages.base_page import BasePage

class ForgotPasswordPage(BasePage):
    """Page Object for the Forgot Password page (/forgot-password) using robust data-test/data-testid attributes."""

    URL = f"{BasePage.BASE_URL}/forgot-password"

    def __init__(self, page: Page):
        super().__init__(page)
        self.section = page.locator('section[data-test="forgot_password_section"], section[data-testid="forgot_password_section"]')
        self.description = page.locator('div[data-test="forget_password_p"], div[data-testid="forget_password_p"]')
        self.email_input = page.locator('input[data-test="email_input"], input[data-testid="email_input"]')
        self.submit_button = page.locator('button[data-test="submit_button"], button[data-testid="submit_button"]')
        self.email_error = page.locator('span[data-test="email_input_errors"], span[data-testid="email_input_errors"]')

    def open(self):
        """Navigate directly to the forgot password page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        return self

    def request_password_reset(self, email: str = ""):
        """Fill in email and submit the reset request."""
        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()
        self.submit_button.click()
        self.page.wait_for_timeout(1000)

    def get_error_message(self) -> str:
        """Return the validation error text displayed under the email input."""
        try:
            self.email_error.wait_for(state="visible", timeout=5000)
            return self.email_error.inner_text().strip()
        except Exception:
            return ""

    def is_form_visible(self) -> bool:
        """Check if essential form components are visible."""
        return (
            self.email_input.is_visible() and
            self.submit_button.is_visible() and
            self.description.is_visible()
        )

