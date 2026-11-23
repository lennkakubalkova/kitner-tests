import pytest
from playwright.sync_api import expect
from pages import LoginPage, CoursesPage
from data.test_data import LogoutData


class TestLogout:
    """Test suite for user logout scenarios according to AGENTS.md rules."""

    def test_user_logout_success(self, page, lector_credentials):
        """
        LGT-01: Successful user logout.
        Steps:
        1. Open login page and sign in with valid credentials.
        2. Verify that user is authenticated (logout button visible).
        3. Perform logout using Page Object method perform_logout().
        4. Assert that user is logged out (login button visible, logout button gone, lector actions gone).
        """
        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        courses_page = CoursesPage(page)
        expect(courses_page.nav_logout).to_be_visible()

        # Akce odhlášení zapouzdřená v Page Objectu
        courses_page.perform_logout()

        # Aserce stavu po odhlášení
        expect(courses_page.nav_login).to_be_visible()
        expect(courses_page.nav_logout).not_to_be_visible()
        expect(courses_page.add_course_button).not_to_be_visible()

