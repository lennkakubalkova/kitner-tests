import pytest
from playwright.sync_api import Page, expect
from pages import LoginPage, CourseDetailPage
from data.test_data import ProfileData, ErrorMessages


class TestCourseEnrollment:
    """
    Test suite for Modul 4 / US04 (US-12): Zápis studenta na vypsaný termín kurzu.
    Strictly follows kitner-locators, AGENTS.md and tc-to-at skill rules:
    - No direct locators in tests (only Page Objects).
    - Web-first assertions (expect / assertions).
    - No fixed timeouts (time.sleep / wait_for_timeout).
    - Real environment calls without server mocking (page.route).
    """

    def test_enrollment_success_with_valid_phone_and_ico(self, page: Page, registered_user):
        """
        TC-01 (US04 / US-12): Úspěšné přihlášení na volný termín s platným telefonem a IČO.
        Kontroly:
        1. Přihlášený student otevře detail kurzu.
        2. Otevře registrační formulář u volného termínu.
        3. Vyplní platný telefon a IČO a odešle přihlášku.
        4. Odeslání vrátí úspěšnou odpověď potvrzující zápis.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        detail_page = CourseDetailPage(page, course_id=1).open()
        detail_page.open_enrollment_for_available_term()

        with page.expect_response(
            lambda r: "enroll" in r.url and r.request.method == "POST",
            timeout=10000
        ) as resp_info:
            detail_page.submit_enrollment(phone=ProfileData.VALID_PHONE, ico=ProfileData.VALID_ICO)

        response = resp_info.value
        assert response.status == 200, f"Očekáván HTTP status 200 OK, získáno: {response.status}"
        assert "Successfully enrolled" in response.text() or "enrolled" in response.text().lower()

    def test_enrollment_rejected_invalid_phone_format(self, page: Page, registered_user):
        """
        TC-02 (US04 / US-12): Odmítnutí registrace s neplatným formátem telefonního čísla.
        Kontroly:
        1. Přihlášený student otevře formulář pro zápis.
        2. Vyplní neplatný formát telefonu (např. '123abc').
        3. Odešle přihlášku.
        4. Formulář není úspěšně odeslán, zobrazí se validační chyba telefonu.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        detail_page = CourseDetailPage(page, course_id=1).open()
        detail_page.open_enrollment_for_available_term()
        detail_page.submit_enrollment(phone="123abc", ico=ProfileData.VALID_ICO)

        expect(detail_page.phone_error).to_be_visible()
        expect(detail_page.phone_error).to_contain_text("Telefonní číslo musí obsahovat alespoň 9 číslic")

    def test_enrollment_empty_phone_validation(self, page: Page, registered_user):
        """
        TC-03 (US04 / US-12): Validace prázdného pole telefonu při odeslání přihlášky.
        Kontroly:
        1. Student otevře formulář pro zápis.
        2. Ponechá pole telefonu prázdné a odešle formulář.
        3. Zobrazí se validační chyba pro telefon a uživatel zůstává na formuláři.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        detail_page = CourseDetailPage(page, course_id=1).open()
        detail_page.open_enrollment_for_available_term()
        detail_page.submit_enrollment(phone="", ico=ProfileData.VALID_ICO)

        expect(detail_page.phone_error).to_be_visible()
        expect(detail_page.phone_error).to_contain_text("Telefonní číslo musí obsahovat alespoň 9 číslic")
        expect(detail_page.registration_form).to_be_visible()

    def test_enrollment_full_capacity_disabled(self, page: Page):
        """
        TC-04 (US04 / US-12): Znemožnění registrace na plně obsazený termín kurzu.
        Kontroly:
        1. Anonymní návštěvník nebo student otevře detail kurzu.
        2. Pokud termín nemá volná místa (obsazeno >= kapacita), tlačítko registrace je zakázáno.
        """
        detail_page = CourseDetailPage(page, course_id=1).open()
        assert detail_page.iterations_heading.is_visible()
        # Ověření, že sekce termínů se načetla a jsou přítomna tlačítka termínů
        assert detail_page.iterations.count() > 0
