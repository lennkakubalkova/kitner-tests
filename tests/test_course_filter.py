import pytest
from playwright.sync_api import Page, expect
from pages import CoursesPage


class TestCourseFilter:
    """
    Test suite for Modul 2 / US03 (US-11): Vyhledávání a filtrování kurzů v katalogu.
    Strictly follows kitner-locators, AGENTS.md and tc-to-at skill rules:
    - No direct locators in tests (only Page Objects).
    - Web-first assertions (expect / assertions).
    - No fixed timeouts (time.sleep / wait_for_timeout).
    - Real environment calls without server mocking (page.route).
    """

    def test_courses_search_by_keyword(self, page: Page):
        """
        TC-01 (US03 / US-11): Úspěšné vyhledání kurzu podle klíčového slova v katalogu.
        Kontroly:
        1. Načtení katalogu kurzů (/courses).
        2. Vyhledání známého klíčového slova (např. 'GIT').
        3. Všechny vrácené výsledky obsahují hledaný výraz.
        4. Počet nalezených kurzů je větší než 0.
        """
        courses_page = CoursesPage(page).open()
        git_courses = courses_page.search_courses("GIT")
        assert len(git_courses) > 0, "V katalogu musí být nalezen alespoň jeden kurz obsahující 'GIT'"
        assert all("git" in name.lower() for name in git_courses), "Všechny nalezené kurzy musí obsahovat 'GIT'"

    def test_courses_filter_by_minimum_capacity(self, page: Page):
        """
        TC-02 (US03 / US-11): Filtrování nabídky kurzů podle minimální volné kapacity.
        Kontroly:
        1. Filtrování kurzů s kapacitou >= 10.
        2. Všechny vyfiltrované kurzy mají kapacitu rovnou nebo vyšší než 10.
        """
        courses_page = CoursesPage(page).open()
        filtered = courses_page.filter_courses_by_capacity(min_capacity=10)
        assert len(filtered) > 0, "V katalogu musí existovat kurzy s kapacitou >= 10"
        assert all(c["capacity"] >= 10 for c in filtered), "Všechny filtrované kurzy musí mít kapacitu >= 10"

    def test_courses_search_nonexistent_keyword(self, page: Page):
        """
        TC-03 (US03 / US-11): Vyhledání neexistujícího výrazu a zobrazení prázdného výsledku.
        Kontroly:
        1. Vyhledání zcela neexistujícího řetězce 'NeexistujiciKurzXYZ999'.
        2. Výsledek vyhledávání neobsahuje žádný kurz.
        """
        courses_page = CoursesPage(page).open()
        results = courses_page.search_courses("NeexistujiciKurzXYZ999")
        assert len(results) == 0, "Vyhledání neexistujícího kurzu musí vrátit prázdný výsledek"

