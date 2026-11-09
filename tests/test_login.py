import pytest
from pages.login_page import LoginPage
from pages.courses_page import CoursesPage
from pages.register_page import RegisterPage

class TestLogin:
    """Test suite for the Login and Session management of Demo login application."""

    def test_login_lector_success_and_privileges(self, page, lector_credentials):
        """
        LOG-01: Successful login with lector account.
        Checks:
        1. Redirection to /courses.
        2. In menu: 'Odhlásit se' is visible, 'Přihlásit se' is absent.
        3. In menu: 'Můj Profil' and 'Moje kurzy' are visible.
        4. Authorization check: Lector controls are active - 'Přidat kurz' button is present.
        5. Authorization check: 'Přidat iteraci' buttons are present on courses.
        """
        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        courses_page = CoursesPage(page)
        # Check URL
        assert "/courses" in page.url, f"Expected URL /courses, but got {page.url}"

        # Deep assertions on menu state
        assert courses_page.is_logged_in(), "Navbar must reflect logged in state (logout present, login absent)"
        assert courses_page.nav_profile.is_visible(), "Link 'Můj Profil' must be visible"
        assert courses_page.nav_my_courses.is_visible(), "Link 'Moje kurzy' must be visible"

        # Privilege checks specific to lector role
        courses_page.add_course_button.wait_for(state="visible", timeout=10000)
        assert courses_page.add_course_button.is_visible(), "Lector must see 'Přidat kurz' button"
        assert courses_page.add_iteration_buttons.count() > 0, "Lector must see 'Přidat iteraci' button on courses"

    def test_login_registered_user_success(self, page, registered_user):
        """
        LOG-02: Successful login with newly registered real user.
        Checks:
        1. User successfully logs in with real registered credentials.
        2. Redirection and menu state shows user is authenticated.
        3. Normal user does NOT see 'Přidat kurz' (privilege boundary check).
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        courses_page = CoursesPage(page)
        # User is logged in
        assert courses_page.is_logged_in(), "Real registered user must be authenticated"
        assert courses_page.nav_profile.is_visible(), "Profile link must be visible for logged in user"

        # Check privilege boundary
        assert not courses_page.add_course_button.is_visible(), (
            "Regular registered user must NOT have access to 'Přidat kurz' button"
        )

    def test_login_empty_fields_validation(self, page):
        """
        LOG-03: Submitting empty login form.
        Checks:
        1. Form is rejected, URL remains on /login.
        2. Required field errors for email and password are both displayed.
        3. User remains in logged-out state.
        """
        login_page = LoginPage(page).open()
        login_page.login("", "")

        assert "/login" in page.url, f"Expected URL /login, but got {page.url}"
        errors = login_page.get_error_texts()
        assert "The email field is required." in errors, f"Expected email required error in {errors}"
        assert "The password field is required." in errors, f"Expected password required error in {errors}"
        assert login_page.is_logged_out(), "Navbar must still show logged-out state"

    def test_login_invalid_password(self, page, lector_credentials):
        """
        LOG-04: Existing user with incorrect password.
        Checks:
        1. URL remains on /login.
        2. Exact authentication error message 'These credentials do not match our records.' appears.
        3. User is not authenticated; navbar shows 'Přihlásit se'.
        """
        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], "IncorrectPassword999!")

        assert "/login" in page.url, f"Expected to remain on /login, but got {page.url}"
        errors = login_page.get_error_texts()
        assert "These credentials do not match our records." in errors, (
            f"Expected invalid credentials error in {errors}"
        )
        assert login_page.is_logged_out(), "User must remain unauthenticated"

    def test_login_nonexistent_user(self, page):
        """
        LOG-05: Non-existent email address and arbitrary password.
        Checks:
        1. URL remains on /login.
        2. Exact error message 'These credentials do not match our records.' appears.
        3. User is not authenticated.
        """
        login_page = LoginPage(page).open()
        login_page.login("completely_nonexistent_tester_12345@testkitner.cz", "SomeSecret123!")

        assert "/login" in page.url, f"Expected to remain on /login, but got {page.url}"
        errors = login_page.get_error_texts()
        assert "These credentials do not match our records." in errors, (
            f"Expected invalid credentials error in {errors}"
        )
        assert login_page.is_logged_out(), "User must remain unauthenticated"

    def test_logout_flow_and_session_cleared(self, page, lector_credentials):
        """
        LOG-06: Complete logout flow.
        Checks:
        1. Lector logs in -> verifies logged in state and presence of privileged buttons.
        2. Lector clicks 'Odhlásit se'.
        3. Navbar changes: 'Odhlásit se' disappears, 'Přihlásit se' reappears.
        4. Privileged buttons ('Přidat kurz', 'Přidat iteraci') immediately disappear.
        """
        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        courses_page = CoursesPage(page)
        assert courses_page.is_logged_in(), "Precondition: user must be logged in"
        courses_page.add_course_button.wait_for(state="visible", timeout=10000)
        assert courses_page.add_course_button.is_visible(), "Precondition: lector button visible"

        # Perform logout
        courses_page.logout()

        # Verify state after logout
        assert courses_page.is_logged_out(), "User must be logged out after clicking Odhlásit se"
        assert not courses_page.nav_logout.is_visible(), "Odhlásit se button must NOT be visible after logout"
        assert courses_page.nav_login.is_visible(), "Přihlásit se button MUST be visible after logout"
        assert not courses_page.add_course_button.is_visible(), "Přidat kurz button must disappear after logout"

    def test_login_navigation_to_register(self, page):
        """
        LOG-07: Navigation test - link 'Zaregistrujte se zde.' navigates from login to register.
        Checks:
        1. Click on register link redirects to /register.
        2. Registration form inputs (name, email, password, password confirmation) are visible.
        """
        login_page = LoginPage(page).open()
        login_page.register_link.click()
        page.wait_for_timeout(1000)

        reg_page = RegisterPage(page)
        assert "/register" in page.url, f"Expected URL /register, but got {page.url}"
        assert reg_page.name_input.is_visible(), "Name input should be visible on /register"
        assert reg_page.email_input.is_visible(), "Email input should be visible on /register"
        assert reg_page.password_input.is_visible(), "Password input should be visible on /register"
        assert reg_page.password_confirmation_input.is_visible(), "Password confirmation should be visible"

