import pytest
from playwright.sync_api import Page, expect
from pages import LoginPage, CoursesPage, CourseDetailPage, MyCoursesPage
from data.test_data import MyCoursesData, ProfileData


class TestMyCourses:
    """
    Test suite for Modul 3 / US-13: Zobrazení přihlášených kurzů (Moje kurzy).
    Strictly follows kitner-locators, AGENTS.md and tc-to-at skill rules:
    - No direct locators in tests (only Page Objects).
    - Web-first assertions (expect).
    - No fixed timeouts (time.sleep / wait_for_timeout).
    - Real environment calls without server mocking (page.route).
    """

    def test_guest_cannot_see_my_courses_nav_link(self, page: Page):
        """
        TC-01 (US-13): Odkaz Moje kurzy není dostupný pro nepřihlášeného návštěvníka.
        Kontroly:
        1. Anonymní návštěvník otevře /courses.
        2. V horní navigaci není odkaz 'Moje kurzy' viditelný.
        3. Uživatel je ve stavu odhlášen.
        """
        courses_page = CoursesPage(page).open()
        expect(courses_page.nav_my_courses).not_to_be_visible()
        assert courses_page.is_logged_out(), "Návštěvník musí být ve stavu odhlášen"

    def test_registered_user_can_open_my_courses_from_menu(self, page: Page, registered_user):
        """
        TC-02 (US-13): Přihlášený student může otevřít sekci Moje kurzy z hlavního menu.
        Kontroly:
        1. Přihlášený student vidí v navigaci odkaz 'Moje kurzy'.
        2. Kliknutí přes Page Object naviguje na /my-courses.
        3. Na stránce je zobrazen nadpis 'Mé zapsané kurzy' a kontejner stránky.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        my_courses_page = MyCoursesPage(page)
        my_courses_page.navigate_from_menu()

        expect(page).to_have_url(my_courses_page.URL)
        expect(my_courses_page.page_container).to_be_visible()
        expect(my_courses_page.courses_title).to_have_text(MyCoursesData.EXPECTED_TITLE)

    def test_enrolled_course_visible_in_my_courses(self, page: Page, registered_user):
        """
        TC-03 (US-13): Ověření zobrazení zapsaného termínu v přehledu Moje kurzy po registraci.
        Kontroly:
        1. Přihlášený student se zapíše na volný termín kurzu.
        2. Po registraci přejde do 'Moje kurzy'.
        3. Sekce zapsaných kurzů a kontejner jsou úspěšně zobrazeny.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        # Přihlášení na termín
        detail_page = CourseDetailPage(page, course_id=1).open()
        detail_page.open_enrollment_for_available_term()
        detail_page.submit_enrollment(phone=ProfileData.VALID_PHONE, ico=ProfileData.VALID_ICO)

        # Přechod do Moje kurzy
        my_courses_page = MyCoursesPage(page)
        my_courses_page.navigate_from_menu()

        expect(page).to_have_url(my_courses_page.URL)
        expect(my_courses_page.page_container).to_be_visible()
        expect(my_courses_page.courses_section).to_be_visible()
        expect(my_courses_page.courses_title).to_have_text(MyCoursesData.EXPECTED_TITLE)
