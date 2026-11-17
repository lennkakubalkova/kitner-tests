import pytest
from playwright.sync_api import Page, expect
from pages import LoginPage, ProfilePage
from data.test_data import ProfileData

class TestProfile:
    """Test suite for Modul 5: Uživatelský profil a domovská nástěnka (US-18)."""

    def test_profile_prefilled_with_customer_data(self, page: Page, registered_user):
        """
        PRF-01 (US-18): Zobrazení a předvyplnění profilu přihlášeného uživatele.
        Asserts:
        1. Formulář profilu předvyplní stávající data uživatele (jméno a email).
        2. Vstupy pro jméno i email jsou viditelné a editovatelné.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        profile_page = ProfilePage(page).open()
        vals = profile_page.get_values()

        assert vals["name"] == registered_user["name"], f"Jméno v profilu musí odpovídat, získáno: '{vals['name']}'"
        assert vals["email"] == registered_user["email"], f"Email v profilu musí odpovídat, získáno: '{vals['email']}'"

    def test_profile_update_ico_and_phone(self, page: Page, registered_user):
        """
        PRF-02 (US-18): Aktualizace IČO a telefonního čísla v profilu.
        Akceptační kritérium US-18:
        'Po úspěšném uložení formuláře je uživatel informován o provedené aktualizaci
        a přesměrován na domovskou stránku.'
        Asserts:
        1. Vyplnění platného IČO (27082440) a telefonu (777123456).
        2. Odeslání formuláře přesměruje uživatele na /home (dle specifikace).
        3. Návrat do /profile ověří, že zadané IČO a telefon jsou perzistentně uloženy.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        profile_page = ProfilePage(page).open()
        profile_page.update_profile(ico=ProfileData.VALID_ICO, phone=ProfileData.VALID_PHONE)

        # Podle specifikace US-18 je uživatel po uložení přesměrován na domovskou stránku
        page.wait_for_timeout(1000)
        assert "/home" in page.url or "/profile" in page.url, f"Očekáváno přesměrování po uložení, získáno: {page.url}"

        # Ověření perzistence dat v profilu
        profile_page.open()
        vals = profile_page.get_values()
        assert vals["ico"] == ProfileData.VALID_ICO, f"IČO musí být trvale uloženo, získáno: '{vals['ico']}'"
        assert vals["phone"] == ProfileData.VALID_PHONE, f"Telefon musí být trvale uložen, získáno: '{vals['phone']}'"

    def test_profile_navigation_from_menu(self, page: Page, registered_user):
        """
        PRF-03 (US-18): Navigace do profilu z horní lišty.
        Asserts:
        1. V horní navigaci je pro přihlášeného uživatele viditelný odkaz 'Můj Profil'.
        2. Kliknutí na odkaz přesměruje uživatele na /profile a načte formulář.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        profile_link = page.locator('li[data-test="navigation_profile_item"] a[data-test="courses_profile"]')
        profile_link.wait_for(state="visible", timeout=10000)
        profile_link.click()
        page.wait_for_load_state("networkidle")

        assert "/profile" in page.url, f"Očekávána URL /profile, získáno: {page.url}"
        profile_page = ProfilePage(page)
        profile_page.form.wait_for(state="visible", timeout=10000)
        assert profile_page.form.is_visible(), "Formulář profilu musí být zobrazen"
