from playwright.sync_api import Page
from pages.base_page import BasePage

class MyCoursesPage(BasePage):
    """Page Object for My Courses page (/my-courses) - US-13."""

    URL = f"{BasePage.BASE_URL}/my-courses"

    def __init__(self, page: Page):
        super().__init__(page)
        self.page_container = page.locator('div[data-test="page_container"]')

    def open(self):
        """Navigate to my courses page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        return self

