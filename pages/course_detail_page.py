from playwright.sync_api import Page
from pages.base_page import BasePage

class CourseDetailPage(BasePage):
    """Page Object for Course Detail page (/courses/{id}) - US-10, US-11, US-16."""

    def __init__(self, page: Page, course_id: int = 1):
        super().__init__(page)
        self.course_id = course_id
        self.URL = f"{BasePage.BASE_URL}/courses/{course_id}"
        self.course_name = page.locator('h1[data-test="course_name"]')
        self.course_description = page.locator('p[data-test="course_description"]')
        self.course_price = page.locator('p[data-test="course_price"]')
        self.iterations_heading = page.locator('h2[data-test="iterations_heading"]')
        self.iterations = page.locator('div[data-test^="iteration_"]')
        self.registration_buttons = page.locator('button[data-test="registration_link"]:has-text("Nezávazná registrace")')
        self.participants_buttons = page.locator('button[data-test="registration_link"]:has-text("Přihlášení")')

        # Enrollment registration form elements (/courses/{id}/register - US-12 / US04)
        self.phone_input = page.locator('input[data-test="phone_input"]')
        self.ico_input = page.locator('input[data-test="ico_input"]')
        self.submit_enrollment_button = page.locator('button[data-test="registration_link"]:has-text("Nezávazná registrace")')

    def open_enrollment_for_available_term(self):
        """Clicks on the first available iteration's 'Nezávazná registrace' button and waits for registration page."""
        self.registration_buttons.first.wait_for(state="visible", timeout=10000)
        self.registration_buttons.first.click()
        self.page.wait_for_url("**/courses/*/register", timeout=10000)
        self.phone_input.wait_for(state="visible", timeout=10000)

    def submit_enrollment(self, phone: str, ico: str | None = None):
        """Fills enrollment form and submits registration for the iteration."""
        self.phone_input.fill(phone)
        if ico:
            self.ico_input.fill(ico)
        self.submit_enrollment_button.click()
        self.page.wait_for_load_state("networkidle")

    def open(self):
        """Navigate directly to course detail."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        try:
            self.course_name.wait_for(state="visible", timeout=10000)
        except Exception:
            pass
        return self

