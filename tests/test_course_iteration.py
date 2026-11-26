import pytest
from playwright.sync_api import Page, expect
from pages import LoginPage, CoursesPage


class TestCourseIteration:
    """
    Test suite for Modul 2 / US05 (US-15): Vypsání nového termínu (iterace) kurzu lektorem.
    Strictly follows kitner-locators, AGENTS.md and tc-to-at skill rules:
    - No direct locators in tests (only Page Objects).
    - Web-first assertions (expect / assertions).
    - No fixed timeouts (time.sleep / wait_for_timeout).
    - Real environment calls without server mocking (page.route).
    """

    def test_lector_can_create_new_course_iteration(self, page: Page, lector_credentials):
        """
        TC-01 (US05 / US-15): Lektor úspěšně vytvoří a vypíše nový termín kurzu.
        Kontroly:
        1. Lektor se přihlásí a otevře přehled kurzů (/courses).
        2. Otevře modál pro vypsání nového termínu ('Přidat iteraci').
        3. Vyplní datum od, datum do, den v týdnu, čas a místo konání.
        4. Odeslání formuláře odešle POST požadavek na /api/courses/{id}/iterations se statusem 201 Created.
        """
        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        courses_page = CoursesPage(page).open()

        with page.expect_response(
            lambda r: "iterations" in r.url and r.request.method == "POST",
            timeout=10000
        ) as resp_info:
            courses_page.create_iteration(
                start_date="2026-12-01",
                end_date="2026-12-15",
                day_index=1,
                time_str="18:00",
                location="Online MS Teams"
            )

        response = resp_info.value
        assert response.status == 201, f"Očekáván HTTP status 201 Created, získáno: {response.status}"

    def test_regular_student_cannot_create_iteration(self, page: Page, registered_user):
        """
        TC-02 (US05 / US-15): Běžný student nemá přístup k vypsání nového termínu kurzu.
        Kontroly:
        1. Uživatel je přihlášen jako běžný student.
        2. V katalogu kurzů (/courses) nejsou viditelná tlačítka pro přidání termínu ('Přidat iteraci').
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        courses_page = CoursesPage(page).open()
        assert courses_page.is_logged_in(), "Uživatel musí být přihlášen"
        assert courses_page.add_iteration_buttons.count() == 0, "Student nesmí vidět tlačítka Přidat iteraci"

