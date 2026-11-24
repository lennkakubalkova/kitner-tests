from playwright.sync_api import Page, expect
from pages.base_page import BasePage

class MyCoursesPage(BasePage):
    """Page Object for My Courses page (/my-courses) - US-13."""

    URL = f"{BasePage.BASE_URL}/my-courses"

    def __init__(self, page: Page):
        super().__init__(page)
        self.page_container = page.locator('div[data-test="page_container"]')
        self.courses_section = page.locator('div[data-test="courses_section"]')
        self.courses_title = page.locator('[data-test="courses_title"]')

    def open(self):
        """Navigate to my courses page."""
        self.page.goto(self.URL)
        expect(self.page_container).to_be_visible()
        return self

    def navigate_from_menu(self):
        """Navigates to my courses by clicking the navbar link."""
        expect(self.nav_my_courses).to_be_visible()
        self.nav_my_courses.click()
        expect(self.page).to_have_url(self.URL)
        expect(self.courses_title).to_be_visible()


