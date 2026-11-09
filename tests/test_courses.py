import time
import pytest
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage

class TestCourses:
    """Test suite for the Courses catalog and Course management functionality using data-test/data-testid."""

    def test_courses_list_visible_for_guest(self, page):
        """
        CRS-01: Anonymní návštěvník vidí katalog kurzů se všemi náležitostmi.
        Kontroly:
        1. Nadpis 'Seznam kurzů' s data-test='courses_title'.
        2. Přítomnost karet kurzů s data-test='course_name', 'course_price', 'course_capacity'.
        3. Tlačítka pro lektora nejsou zobrazena.
        """
        courses_page = CoursesPage(page).open()
        
        assert courses_page.courses_title.is_visible(), "Nadpis kurzů musí být viditelný"
        assert courses_page.course_cards.count() > 0, "V katalogu musí být alespoň jeden kurz"
        assert courses_page.course_names.first.is_visible(), "Název kurzu musí být zobrazen"
        assert courses_page.course_prices.first.is_visible(), "Cena kurzu musí být zobrazena"
        assert courses_page.course_capacities.first.is_visible(), "Kapacita kurzu musí být zobrazena"
        
        # Kontrola, že anonym nemá práva lektora
        assert not courses_page.add_course_button.is_visible(), "Anonym nesmí vidět tlačítko Přidat kurz"
        assert courses_page.add_iteration_buttons.count() == 0, "Anonym nesmí vidět tlačítka Přidat iteraci"

    def test_regular_user_cannot_access_course_management(self, page, registered_user):
        """
        CRS-02: Běžně zaregistrovaný uživatel nemá přístup ke správě kurzů.
        Kontroly:
        1. Uživatel je přihlášen.
        2. Tlačítko 'Přidat kurz' a 'Přidat iteraci' zůstávají skrytá.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        courses_page = CoursesPage(page).open()
        assert courses_page.is_logged_in(), "Uživatel musí být přihlášen"
        assert not courses_page.add_course_button.is_visible(), "Student nesmí vidět tlačítko Přidat kurz"
        assert courses_page.add_iteration_buttons.count() == 0, "Student nesmí vidět tlačítka Přidat iteraci"

    def test_lector_can_open_create_course_modal(self, page, lector_credentials):
        """
        CRS-03: Lektor může otevřít modální okno pro vytvoření kurzu.
        Kontroly:
        1. Klik na tlačítko 'Přidat kurz'.
        2. Zobrazení modálního kontejneru data-test='course_form_container'.
        3. Přítomnost všech formulářových prvků (název, popis, kapacita, cena, tlačítko vytvořit).
        """
        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        courses_page = CoursesPage(page).open()
        assert courses_page.add_course_button.is_visible(), "Lektor musí vidět tlačítko Přidat kurz"

        courses_page.add_course_button.click()
        page.wait_for_timeout(1000)

        assert courses_page.modal_container.is_visible(), "Modální okno musí být zobrazeno"
        assert courses_page.modal_name_input.is_visible(), "Pole pro název kurzu musí být viditelné"
        assert courses_page.modal_description_input.is_visible(), "Pole pro popis kurzu musí být viditelné"
        assert courses_page.modal_capacity_input.is_visible(), "Pole pro kapacitu musí být viditelné"
        assert courses_page.modal_price_input.is_visible(), "Pole pro cenu musí být viditelné"
        assert courses_page.modal_submit_button.is_visible(), "Tlačítko Vytvořit kurz musí být viditelné"

    def test_lector_can_create_new_course(self, page, lector_credentials):
        """
        CRS-04: Lektor úspěšně vytvoří nový kurz.
        Kontroly:
        1. Vyplnění a odeslání kurzu s unikátním názvem.
        2. Ověření, že nový kurz se objevil v přehledu kurzů na stránce.
        """
        ts = int(time.time())
        course_name = f"QA Kurz {ts}"
        course_desc = "Komplexni kurz automatizace testovani s Playwright a pytest."
        course_capacity = 16
        course_price = 3990

        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        courses_page = CoursesPage(page).open()
        courses_page.create_course(
            name=course_name,
            description=course_desc,
            capacity=course_capacity,
            price=course_price
        )

        # Ověření, že nový kurz byl vytvořen a nachází se v přehledu kurzů
        courses_page.open()
        page.wait_for_selector('h2[data-test="course_name"]', timeout=10000)
        page.wait_for_timeout(1000)
        all_course_names = [el.inner_text().strip() for el in courses_page.course_names.all()]
        assert any(course_name in name for name in all_course_names), (
            f"Nově vytvořený kurz '{course_name}' musí být nalezen v seznamu kurzů. Celkem nalezeno: {len(all_course_names)} kurzů."
        )
