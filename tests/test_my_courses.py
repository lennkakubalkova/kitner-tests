import pytest
from playwright.sync_api import Page, expect
from pages import LoginPage, MyCoursesPage

class TestMyCourses:
    """Test suite for Modul 3: Zápis a Moje kurzy (US-13)."""

    def test_my_courses_accessible_from_navigation(self, page: Page, registered_user):
        """
        MYC-01 (US-13): Sekce 'Moje kurzy' je přístupná z navigace pro přihlášené zákazníky.
        Asserts:
        1. V horní navigaci je po přihlášení dostupná volba 'Moje kurzy'.
        2. Kliknutí na odkaz přesměruje uživatele na /my-courses.
        3. Stránka se korektně načte bez chyb.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        my_courses_link = page.locator('a[data-test="courses_link"]:has-text("Moje kurzy")')
        my_courses_link.wait_for(state="visible", timeout=10000)
        my_courses_link.click()
        page.wait_for_load_state("networkidle")

        assert "/my-courses" in page.url, f"Očekávána URL /my-courses, získáno: {page.url}"
        my_courses_page = MyCoursesPage(page)
        assert my_courses_page.page_container.is_visible(), "Kontejner stránky Moje kurzy musí být zobrazen"

