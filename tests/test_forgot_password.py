import pytest
from playwright.sync_api import Page, expect
from pages import LoginPage, ForgotPasswordPage
from data.test_data import ErrorMessages, StatusMessages
from utils.helpers import generate_unique_email

class TestForgotPassword:
    """Test suite for Forgot Password module (US-05)."""

    def test_navigation_from_login_to_forgot_password(self, page: Page):
        """
        RST-01 (US-05): Ověření přechodu z přihlašovací stránky na formulář zapomenutého hesla.
        Asserts:
        1. Kliknutí na odkaz 'Zapomněli jste heslo?' přesměruje na /forgot-password.
        2. Popisný text formuláře 'Zapoměli jste své heslo?...' je viditelný.
        3. Pole pro zadání e-mailu 'email_input' je přítomno a viditelné.
        4. Odesílací tlačítko 'submit_button' je přítomno a viditelné.
        5. Globální navigace (Navbar) zůstává plně funkční.
        """
        login_page = LoginPage(page).open()
        assert login_page.forgot_password_link.is_visible(), "Odkaz na zapomenuté heslo musí být na stránce loginu viditelný"
        
        login_page.click_forgot_password()
        
        forgot_page = ForgotPasswordPage(page)
        expect(page).to_have_url(forgot_page.URL)
        assert forgot_page.is_form_visible(), "Formulář zapomenutého hesla musí mít viditelný popis, input i tlačítko"
        assert "Zapoměli jste své heslo?" in forgot_page.description.inner_text(), "Popisný text formuláře musí odpovídat"
        assert forgot_page.navigation.is_visible(), "Globální navigace musí zůstat přítomna"

    def test_forgot_password_empty_email_validation(self, page: Page):
        """
        RST-02 (US-05): Ověření validace prázdného pole při žádosti o obnovu hesla.
        Asserts:
        1. URL zůstává na /forgot-password.
        2. Zobrazí se validační chyba 'The email field is required.'.
        3. Chybová hláška je v elementu span[data-test='email_input_errors'].
        """
        forgot_page = ForgotPasswordPage(page).open()
        forgot_page.request_password_reset("")
        
        expect(page).to_have_url(forgot_page.URL)
        error_msg = forgot_page.get_error_message()
        assert ErrorMessages.REQUIRED_EMAIL in error_msg, f"Očekávána chyba prázdného pole, získáno: '{error_msg}'"

    def test_forgot_password_nonexistent_email_validation(self, page: Page):
        """
        RST-03 (US-05): Ověření odmítnutí neexistujícího uživatele při obnově hesla.
        Asserts:
        1. URL zůstává na /forgot-password.
        2. Zobrazí se chybová hláška 'We can't find a user with that email address.'.
        3. Systém nezhroutí aplikaci.
        """
        forgot_page = ForgotPasswordPage(page).open()
        nonexistent_email = generate_unique_email(prefix="nonexistent")
        forgot_page.request_password_reset(nonexistent_email)
        
        expect(page).to_have_url(forgot_page.URL)
        error_msg = forgot_page.get_error_message()
        assert ErrorMessages.USER_NOT_FOUND in error_msg, f"Očekávána chyba neexistujícího emailu, získáno: '{error_msg}'"

    def test_forgot_password_registered_user_submission(self, page: Page, lector_credentials):
        """
        RST-04 (US-05): Ověření odeslání požadavku na obnovu hesla pro registrovaného uživatele.
        Akceptační kritérium US-05:
        'Po odeslání platné žádosti systém vygeneruje bezpečný, časově omezený resetovací odkaz
        a v rozhraní zobrazí potvrzení o odeslání požadavku.'
        Kontroly (reálné volání serveru bez simulace):
        1. Odeslání formuláře s platným e-mailem registrovaného uživatele.
        2. V rozhraní aplikace se zobrazí potvrzovací hláška 'We have emailed your password reset link!'.
        3. Potvrzovací hláška je viditelná v elementu div[data-test='status_div'].
        """
        forgot_page = ForgotPasswordPage(page).open()
        forgot_page.request_password_reset(lector_credentials["email"])

        status_text = forgot_page.get_status_message()
        assert StatusMessages.RESET_PASSWORD_SUCCESS in status_text, (
            f"Očekávána potvrzovací zpráva '{StatusMessages.RESET_PASSWORD_SUCCESS}', získáno: '{status_text}'"
        )
        assert forgot_page.status_message.is_visible(), "Potvrzovací element status_div musí být v rozhraní viditelný"
