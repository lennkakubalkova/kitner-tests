from playwright.sync_api import Page
from pages.base_page import BasePage

class CoursesPage(BasePage):
    """Page Object for the Courses overview page (/courses)."""

    URL = f"{BasePage.BASE_URL}/courses"

    def __init__(self, page: Page):
        super().__init__(page)
        self.add_course_button = page.locator('button:has-text("Přidat kurz")')
        self.add_iteration_buttons = page.locator('button:has-text("Přidat iteraci")')
        self.courses_heading = page.locator('h1, h2:has-text("Seznam kurzů")')

    def open(self):
        """Navigate to the courses page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        return self

    def has_lector_controls(self) -> bool:
        """Returns True if lector-specific controls (add course, add iteration) are visible."""
        return self.add_course_button.is_visible() and self.add_iteration_buttons.count() > 0

