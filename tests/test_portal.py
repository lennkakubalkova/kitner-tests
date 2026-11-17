import pytest
from playwright.sync_api import Page, expect
from pages import PortalPage

class TestPortal:
    """Test suite for Modul 0: Úvodní navigační rozcestník (US-01)."""

    def test_portal_navigation_links_present_and_valid(self, page: Page):
        """
        POR-01 (US-01): Úvodní navigační rozcestník testovacích aplikací.
        Asserts:
        1. Titulek stránky obsahuje 'Testování'.
        2. Přítomen funkční odkaz na Kalkulačku.
        3. Přítomen funkční odkaz na Testovací login.
        4. Přítomen funkční odkaz na NextDate.
        5. Přítomen funkční odkaz na Registraci na kurz včetně výpisu.
        6. Přítomen výrazný odkaz pro vstup do aplikace kurzů ('Demo-login').
        """
        portal = PortalPage(page).open()
        
        assert "Testování" in page.title(), f"Očekáván titulek s 'Testování', získáno: {page.title()}"
        assert portal.kalkulacka_link.is_visible(), "Rozcestník musí obsahovat odkaz na Kalkulačku"
        assert portal.login_app_link.is_visible(), "Rozcestník musí obsahovat odkaz na Testovací login"
        assert portal.nextdate_link.is_visible(), "Rozcestník musí obsahovat odkaz na NextDate"
        assert portal.regkurz_link.is_visible(), "Rozcestník musí obsahovat odkaz na Registraci na kurz"
        assert portal.regkurz_vypis_link.is_visible(), "Rozcestník musí obsahovat odkaz na výpis registrací"
        assert portal.demo_login_link.is_visible(), "Rozcestník musí obsahovat odkaz na Demo-login"

    def test_portal_demo_login_link_navigates_to_courses(self, page: Page):
        """
        POR-02 (US-01): Přechod z rozcestníku do aplikace kurzů.
        Asserts:
        1. Kliknutí na odkaz 'Demo-login' přesměruje návštěvníka přímo do katalogu kurzů (/courses).
        2. V katalogu kurzů se načte a zobrazí nadpis 'Seznam kurzů'.
        """
        portal = PortalPage(page).open()
        portal.demo_login_link.click()
        page.wait_for_load_state("networkidle")
        
        assert "/courses" in page.url, f"Očekávána cílová adresa /courses, získáno: {page.url}"
        courses_title = page.locator('h1[data-test="courses_title"]')
        courses_title.wait_for(state="visible", timeout=10000)
        assert courses_title.is_visible(), "Na stránce kurzů musí být viditelný nadpis Seznam kurzů"
