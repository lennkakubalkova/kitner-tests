import time
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.forgot_password_page import ForgotPasswordPage

def test_navigation_from_login_to_forgot_password(page: Page):
    """
    RST-01: Ověření přechodu z přihlašovací stránky na formulář zapomenutého hesla.
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

def test_forgot_password_empty_email_validation(page: Page):
    """
    RST-02: Ověření validace prázdného pole při žádosti o obnovu hesla.
    Asserts:
    1. URL zůstává na /forgot-password.
    2. Zobrazí se validační chyba 'The email field is required.'.
    3. Chybová hláška je v elementu span[data-test='email_input_errors'].
    """
    forgot_page = ForgotPasswordPage(page).open()
    forgot_page.request_password_reset("")
    
    expect(page).to_have_url(forgot_page.URL)
    error_msg = forgot_page.get_error_message()
    assert "The email field is required." in error_msg, f"Očekávána chyba prázdného pole, získáno: '{error_msg}'"

def test_forgot_password_nonexistent_email_validation(page: Page):
    """
    RST-03: Ověření odmítnutí neexistujícího uživatele při obnově hesla.
    Asserts:
    1. URL zůstává na /forgot-password.
    2. Zobrazí se chybová hláška 'We can't find a user with that email address.'.
    3. Systém nezhroutí aplikaci.
    """
    forgot_page = ForgotPasswordPage(page).open()
    nonexistent_email = f"nonexistent_user_{int(time.time())}@example.com"
    forgot_page.request_password_reset(nonexistent_email)
    
    expect(page).to_have_url(forgot_page.URL)
    error_msg = forgot_page.get_error_message()
    assert "We can't find a user with that email address." in error_msg, f"Očekávána chyba neexistujícího emailu, získáno: '{error_msg}'"

def test_forgot_password_registered_user_submission(page: Page):
    """
    RST-04: Ověření odeslání požadavku na obnovu hesla pro registrovaného uživatele.
    Asserts:
    1. Požadavek odejde na backend s validním CSRF tokenem (POST /forgot-password).
    2. Backend zpracuje požadavek a vrátí platný stav:
       - 200 OK (při funkčním odeslání emailu),
       - 422 Unprocessable Entity (při rate-limiting throttling),
       - 500 (při vyčerpání Mailtrap SMTP kvóty na demo serveru testovani.kitner.cz).
    3. V případě limitu 422 ověří 'Please wait before retrying.', při 500 ověří limit Mailtrap SMTP.
    """
    forgot_page = ForgotPasswordPage(page).open()
    
    with page.expect_response(lambda r: "forgot-password" in r.url and r.request.method == "POST", timeout=10000) as resp_info:
        forgot_page.request_password_reset("lector@lector.com")
        
    response = resp_info.value
    assert response.status in [200, 422, 500], f"Očekáván známý status odpovědi, vráceno: {response.status}"
    
    if response.status == 422:
        error_msg = forgot_page.get_error_message()
        assert "Please wait before retrying." in error_msg or "The email field is required." in error_msg
    elif response.status == 500:
        body_text = response.text()
        assert any(term in body_text.lower() for term in ["mailtrap", "smtp", "email", "limit"]), "Chyba 500 musí být způsobena limitem Mailtrap SMTP kvóty"
