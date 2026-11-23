import pytest
from playwright.sync_api import expect
from pages import LoginPage, CoursesPage
from config.config import Config


class TestNavigation:
    """
    Test suite for verifying navigation links according to kitner-locators skill and AGENTS.md.
    Strictly uses data-test/data-testid attributes and Page Object encapsulation.
    """

    def test_navigate_to_home_page_via_navbar(self, page, lector_credentials):
        """
        NAV-01: Verify navigation to /home via navbar Home link.
        Steps:
        1. Log in with valid credentials to make navbar links available.
        2. Verify that 'nav_home' link (using data-test="home_link") is visible.
        3. Click 'nav_home' via Page Object method click_home_navigation().
        4. Assert that page redirects to /home.
        """
        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        courses_page = CoursesPage(page)
        expect(courses_page.nav_home).to_be_visible()

        # Interakce přes metodu Page Objectu
        courses_page.click_home_navigation()

        # Aserce bez přímých selektorů
        expect(page).to_have_url(f"{Config.BASE_URL}/home")
