import pytest
from pages import RegisterPage, HomePage, LoginPage, CoursesPage
from data.test_data import ErrorMessages, UserData
from utils.helpers import generate_unique_email, generate_user_data

class TestRegistration:
    """Test suite for the Registration functionality of Demo login application."""

    def test_registration_success_verifies_login_state_and_welcome(self, page):
        """
        TC-01 / REG-01 (US-02, US-17): Positive registration of a new user.
        Checks:
        1. Redirection to /home.
        2. Welcome banner displays user's name ('Vítej uživateli <name>!').
        3. Navbar confirms logged in state: 'Odhlásit se', 'Můj Profil' and 'Moje kurzy' visible.
        4. Navbar 'Přihlásit se' is absent.
        5. Normal user does not have lector-only controls ('Přidat kurz').
        """
        user_data = generate_user_data(name_prefix="Jan Novák")

        reg_page = RegisterPage(page).open()
        reg_page.register(
            name=user_data["name"],
            email=user_data["email"],
            password=user_data["password"],
            password_confirmation=user_data["password_confirmation"]
        )

        home_page = HomePage(page)
        assert "/home" in page.url, f"Expected URL /home, but got {page.url}"
        
        # Verify user greeting
        welcome_text = home_page.get_welcome_text()
        assert user_data["name"] in welcome_text, f"Expected user name in welcome banner, got '{welcome_text}'"
        assert "Vítej uživateli" in welcome_text, f"Expected greeting prefix in '{welcome_text}'"

        # Verify menu reflects logged-in state
        assert home_page.is_logged_in(), "User should be marked as logged in"
        assert home_page.nav_profile.is_visible(), "Link 'Můj Profil' must be visible in menu"
        assert home_page.nav_my_courses.is_visible(), "Link 'Moje kurzy' must be visible in menu"

        # Verify regular user has no lector privileges
        courses_page = CoursesPage(page)
        assert not courses_page.add_course_button.is_visible(), "Regular user should NOT see 'Přidat kurz' button"

    def test_registration_empty_form_validation(self, page):
        """
        TC-02 / REG-02 (US-02): Submitting empty registration form.
        Checks:
        1. User stays on /register.
        2. Required field errors for name, email, and password appear.
        3. User is not logged in.
        """
        reg_page = RegisterPage(page).open()
        reg_page.register(name="", email="", password="", password_confirmation="")

        assert "/register" in page.url, f"Expected to remain on /register, but got {page.url}"
        errors = reg_page.get_error_texts()
        assert ErrorMessages.REQUIRED_NAME in errors, f"Expected name error in {errors}"
        assert ErrorMessages.REQUIRED_EMAIL in errors, f"Expected email error in {errors}"
        assert ErrorMessages.REQUIRED_PASSWORD in errors, f"Expected password error in {errors}"
        assert reg_page.is_logged_out(), "User must remain in logged-out state"

    def test_registration_password_mismatch(self, page):
        """
        TC-03 / REG-03 (US-02): Password confirmation does not match password.
        Checks:
        1. Form is rejected, URL remains /register.
        2. Confirmation mismatch error appears.
        3. User is not logged in.
        """
        email = generate_unique_email(prefix="mismatch")
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name="Mismatch User",
            email=email,
            password="PrimaryPassword123!",
            password_confirmation="DifferentPassword999!"
        )

        assert "/register" in page.url, f"Expected to remain on /register, but got {page.url}"
        errors = reg_page.get_error_texts()
        assert ErrorMessages.PASSWORD_CONFIRMATION_MISMATCH in errors, (
            f"Expected confirmation mismatch error in {errors}"
        )
        assert reg_page.is_logged_out(), "User must not be logged in after failed registration"

    def test_registration_duplicate_email(self, page, lector_credentials):
        """
        TC-04 / REG-04 (US-02): Attempting to register with an already existing email.
        Checks:
        1. Application rejects duplicate registration.
        2. Error message 'The email has already been taken.' appears.
        3. User remains in logged-out state.
        """
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name="Duplicate Registrant",
            email=lector_credentials["email"],
            password=UserData.DEFAULT_PASSWORD,
            password_confirmation=UserData.DEFAULT_PASSWORD
        )

        assert "/register" in page.url, f"Expected to stay on /register, but got {page.url}"
        errors = reg_page.get_error_texts()
        assert ErrorMessages.EMAIL_ALREADY_TAKEN in errors, f"Expected duplicate email error in {errors}"
        assert reg_page.is_logged_out(), "User must not be logged in"

    def test_registration_missing_name_only(self, page):
        """
        REG-05 (US-02): Missing only the user name.
        Checks:
        1. Only 'The name field is required.' is reported.
        2. No spurious email or password errors.
        3. User is not logged in.
        """
        email = generate_unique_email(prefix="noname")
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name="",
            email=email,
            password=UserData.DEFAULT_PASSWORD,
            password_confirmation=UserData.DEFAULT_PASSWORD
        )

        assert "/register" in page.url
        errors = reg_page.get_error_texts()
        assert ErrorMessages.REQUIRED_NAME in errors, f"Expected name required error in {errors}"
        assert ErrorMessages.REQUIRED_EMAIL not in errors, "Email was filled, should not show error"
        assert ErrorMessages.REQUIRED_PASSWORD not in errors, "Password was filled, should not show error"
        assert reg_page.is_logged_out()

    def test_registration_missing_password_only(self, page):
        """
        REG-06 (US-02): Missing password fields while name and email are filled.
        Checks:
        1. Only 'The password field is required.' is reported.
        2. Name and email errors are not present.
        3. User is not logged in.
        """
        email = generate_unique_email(prefix="nopass")
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name="No Password User",
            email=email,
            password="",
            password_confirmation=""
        )

        assert "/register" in page.url
        errors = reg_page.get_error_texts()
        assert ErrorMessages.REQUIRED_PASSWORD in errors, f"Expected password required error in {errors}"
        assert ErrorMessages.REQUIRED_NAME not in errors, "Name was filled, should not show error"
        assert ErrorMessages.REQUIRED_EMAIL not in errors, "Email was filled, should not show error"
        assert reg_page.is_logged_out()

    def test_registration_link_navigates_to_login(self, page):
        """
        REG-07 (US-02): Navigation test - link 'Zde se přihlaste.' navigates from register to login.
        Checks:
        1. Click on login link redirects to /login.
        2. Login input fields are present and interactive.
        """
        reg_page = RegisterPage(page).open()
        reg_page.login_link.click()
        login_page = LoginPage(page)
        login_page.email_input.wait_for(state="visible", timeout=5000)

        assert "/login" in page.url, f"Expected URL /login, but got {page.url}"
        assert login_page.email_input.is_visible(), "Email input should be visible on /login"
        assert login_page.password_input.is_visible(), "Password input should be visible on /login"

    def test_registration_duplicate_email_case_insensitive(self, page, lector_credentials):
        """
        REG-08 (US-02): Unikátnost emailu je necitlivá na velikost písmen a mezery.
        Akceptační kritérium US-02:
        'Zadaný e-mail je před validací normalizován (odstranění mezer na začátku a konci)
        a systém je při ověřování unikátnosti necitlivý na velikost písmen.'
        Kontroly:
        1. Pokus o registraci s '  LECTOR@LECTOR.COM  '.
        2. Chybová hláška 'The email has already been taken.'.
        3. Uživatel není zaregistrován a zůstává nepřihlášen.
        """
        spaced_upper_email = f"  {lector_credentials['email'].upper()}  "
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name="Duplicitni User",
            email=spaced_upper_email,
            password=UserData.DEFAULT_PASSWORD,
            password_confirmation=UserData.DEFAULT_PASSWORD
        )

        assert "/register" in page.url
        errors = reg_page.get_error_texts()
        assert ErrorMessages.EMAIL_ALREADY_TAKEN in errors, f"Očekávána chyba duplicity emailu, získáno: {errors}"
        assert reg_page.is_logged_out(), "Uživatel nesmí být přihlášen"

    def test_registration_invalid_email_format(self, page):
        """
        REG-09 (US01 / US-02): Validace nesprávného formátu e-mailu při registraci.
        Kontroly:
        1. Zadání neplatného formátu e-mailu ('neplatny_email_bez_zavinace').
        2. Registrace je zamítnuta a uživatel zůstává na /register.
        3. Uživatel není přihlášen.
        """
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name="Invalid Email User",
            email="neplatny_email_bez_zavinace",
            password=UserData.DEFAULT_PASSWORD,
            password_confirmation=UserData.DEFAULT_PASSWORD
        )

        assert "/register" in page.url, f"Očekáváno setrvání na /register, získáno: {page.url}"
        assert reg_page.is_logged_out(), "Uživatel nesmí být přihlášen s neplatným formátem emailu"

    def test_registration_empty_password_confirmation(self, page):
        """
        REG-10 (US01 / US-02): Validace prázdného pole 'Heslo znovu'.
        Kontroly:
        1. Vyplnění jména, unikátního e-mailu a hesla, ale pole 'Heslo znovu' zůstane prázdné.
        2. Registrace je zamítnuta (zobrazí se chybová hláška pro neshodu/potvrzení hesla).
        3. Uživatel zůstává nepřihlášen na /register.
        """
        email = generate_unique_email(prefix="noconfirm")
        reg_page = RegisterPage(page).open()
        reg_page.register(
            name="No Confirm User",
            email=email,
            password=UserData.DEFAULT_PASSWORD,
            password_confirmation=""
        )

        assert "/register" in page.url, f"Očekáváno setrvání na /register, získáno: {page.url}"
        errors = reg_page.get_error_texts()
        assert ErrorMessages.PASSWORD_CONFIRMATION_MISMATCH in errors, (
            f"Očekávána chyba neshody/potvrzení hesla v {errors}"
        )
        assert reg_page.is_logged_out(), "Uživatel nesmí být přihlášen s nevyplněným potvrzením hesla"
