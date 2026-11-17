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

    def open(self):
        """Navigate directly to course detail."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        try:
            self.course_name.wait_for(state="visible", timeout=10000)
        except Exception:
            pass
        return self

