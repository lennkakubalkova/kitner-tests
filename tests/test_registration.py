import time
import pytest
from pages.register_page import RegisterPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.courses_page import CoursesPage

class TestRegistration:
    """Test suite for the Registration functionality of Demo login application."""

    def test_registration_success_verifies_login_state_and_welcome(self, page):
        """
        REG-01: Positive registration of a new user.
        Checks:
        1. Redirection to /home.
        2. Welcome banner displays user's name ('Vítej uživateli <name>!').
        3. Navbar confirms logged in state: 'Odhlásit se', 'Můj Profil' and 'Moje kurzy' visible.
        4. Navbar 'Přihlásit se' is absent.
        5. Normal user does not have lector-only controls ('Přidat kurz').
        """
        ts = int(time.time() * 1000)
        user_name = f"Jan Novák {ts}"
        user_email = f"jan.novak.{ts}@testkitner.cz"
        user_password = "SecurePassword123!"

        reg_page = RegisterPage(page).open()
        reg_page.register(
            name=user_name,
            email=user_email,
            password=user_password,
            password_confirmation=user_password
        )

        home_page = HomePage(page)
        # Multi-layer assertions
        assert "/home" in page.url, f"Expected URL /home, but got {page.url}"
        
        # Verify user greeting
        welcome_text = home_page.get_welcome_text()
        assert user_name in welcome_text, f"Expected user name '{user_name}' in welcome banner, got '{welcome_text}'"
        assert "Vítej uživateli" in welcome_text, f"Expected greeting prefix in '{welcome_text}'"

        # Verify menu reflects logged-in state
        assert home_page.is_logged_in(), "User should be marked as logged in (Odhlásit se present, Přihlásit se absent)"
        assert home_page.nav_profile.is_visible(), "Link 'Můj Profil' must be visible in menu"
        assert home_page.nav_my_courses.is_visible(), "Link 'Moje kurzy' must be visible in menu"

        # Verify regular user has no lector privileges
        courses_page = CoursesPage(page)
        assert not courses_page.add_course_button.is_visible(), "Regular user should NOT see 'Přidat kurz' button"

    def test_registration_empty_form_validation(self, page):
        """
        REG-02: Submitting an empty registration form.
        Checks:
        1. Form is not submitted, URL stays on /register.
        2. Three separate required field validation errors appear.
        3. User is not logged in.
        """
        reg_page = RegisterPage(page).open()
        reg_page.register("", "", "", "")

        assert "/register" in page.url, f"Expected to remain on /register, but got {page.url}"
        errors = reg_page.get_error_texts()

        assert "The name field is required." in errors, f"Missing name validation error in {errors}"
        assert "The email field is required." in errors, f"Missing email validation error in {errors}"
        assert "The password field is required." in errors, f"Missing password validation error in {errors}"
        assert reg_page.is_logged_out(), "User should remain logged out"

    def test_registration_password_mismatch(self, page):
        """
        REG-03: Password and password confirmation do not match.
        Checks:
        1. URL remains on /register.
        2. Exact validation message 'The password field confirmation does not match.' is displayed.
        3. User is not logged in.
        """
        ts = int(time.time() * 1000)
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name=f"Mismatch Tester {ts}",
            email=f"mismatch_{ts}@testkitner.cz",
            password="Password123!",
            password_confirmation="DifferentPassword456!"
        )

        assert "/register" in page.url, f"Expected to remain on /register, but got {page.url}"
        errors = reg_page.get_error_texts()
        assert "The password field confirmation does not match." in errors, (
            f"Expected password mismatch error in {errors}"
        )
        assert reg_page.is_logged_out(), "User should remain logged out"

    def test_registration_duplicate_email(self, page, lector_credentials):
        """
        REG-04: Attempt to register with an already existing email address.
        Checks:
        1. URL remains on /register.
        2. Exact backend error 'The email has already been taken.' is displayed.
        3. User is not logged in.
        """
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name="Duplicate User",
            email=lector_credentials["email"],
            password="SomePassword123!",
            password_confirmation="SomePassword123!"
        )

        assert "/register" in page.url, f"Expected to remain on /register, but got {page.url}"
        errors = reg_page.get_error_texts()
        assert "The email has already been taken." in errors, (
            f"Expected duplicate email error in {errors}"
        )
        assert reg_page.is_logged_out(), "User should remain logged out"

    def test_registration_missing_name_only(self, page):
        """
        REG-05: Missing only the user name.
        Checks:
        1. Only 'The name field is required.' is reported.
        2. No spurious email or password errors.
        3. User is not logged in.
        """
        ts = int(time.time() * 1000)
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name="",
            email=f"noname_{ts}@testkitner.cz",
            password="ValidPassword123!",
            password_confirmation="ValidPassword123!"
        )

        assert "/register" in page.url
        errors = reg_page.get_error_texts()
        assert "The name field is required." in errors, f"Expected name required error in {errors}"
        assert "The email field is required." not in errors, "Email was filled, should not show error"
        assert "The password field is required." not in errors, "Password was filled, should not show error"
        assert reg_page.is_logged_out()

    def test_registration_missing_password_only(self, page):
        """
        REG-06: Missing password fields while name and email are filled.
        Checks:
        1. Only 'The password field is required.' is reported.
        2. Name and email errors are not present.
        3. User is not logged in.
        """
        ts = int(time.time() * 1000)
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name=f"No Password User {ts}",
            email=f"nopass_{ts}@testkitner.cz",
            password="",
            password_confirmation=""
        )

        assert "/register" in page.url
        errors = reg_page.get_error_texts()
        assert "The password field is required." in errors, f"Expected password required error in {errors}"
        assert "The name field is required." not in errors, "Name was filled, should not show error"
        assert "The email field is required." not in errors, "Email was filled, should not show error"
        assert reg_page.is_logged_out()

    def test_registration_link_navigates_to_login(self, page):
        """
        REG-07: Navigation test - link 'Přihlašte se zde.' navigates from register to login.
        Checks:
        1. Click on login link redirects to /login.
        2. Login input fields are present and interactive.
        """
        reg_page = RegisterPage(page).open()
        reg_page.login_link.click()
        page.wait_for_timeout(1000)

        login_page = LoginPage(page)
        assert "/login" in page.url, f"Expected URL /login, but got {page.url}"
        assert login_page.email_input.is_visible(), "Email input should be visible on /login"
        assert login_page.password_input.is_visible(), "Password input should be visible on /login"

