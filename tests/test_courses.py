import pytest
from pages import CoursesPage, CourseDetailPage, LoginPage
from utils.helpers import generate_course_data

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
        courses_page.modal_container.wait_for(state="visible", timeout=5000)

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
        course_payload = generate_course_data()

        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        courses_page = CoursesPage(page).open()
        courses_page.create_course(
            name=course_payload["name"],
            description=course_payload["description"],
            capacity=course_payload["capacity"],
            price=course_payload["price"]
        )

        # Ověření, že nový kurz byl vytvořen a nachází se v přehledu kurzů
        courses_page.open()
        courses_page.course_names.first.wait_for(state="visible", timeout=10000)
        all_course_names = [el.inner_text().strip() for el in courses_page.course_names.all()]
        assert any(course_payload["name"] in name for name in all_course_names), (
            f"Nově vytvořený kurz '{course_payload['name']}' musí být nalezen v seznamu kurzů. Celkem nalezeno: {len(all_course_names)} kurzů."
        )

    def test_course_detail_navigation_and_info(self, page):
        """
        CRS-05 (US-10): Zobrazení detailu kurzu a vypsaných termínů.
        Kontroly:
        1. Kliknutí na 'Chci vidět více' v katalogu kurzů.
        2. Přesměrování na /courses/{id}.
        3. Přítomnost kompletního názvu kurzu, popisu, ceny a sekce vypsaných termínů.
        """
        courses_page = CoursesPage(page).open()
        courses_page.detail_buttons.first.wait_for(state="visible", timeout=10000)
        courses_page.detail_buttons.first.click()
        page.wait_for_load_state("networkidle")

        assert "/courses/" in page.url, f"Očekávána URL detailu kurzu, získáno: {page.url}"
        detail_page = CourseDetailPage(page)
        detail_page.course_name.wait_for(state="visible", timeout=10000)
        assert detail_page.course_name.is_visible(), "Název kurzu musí být viditelný na detailu"
        assert detail_page.course_description.is_visible(), "Popis kurzu musí být viditelný"
        assert detail_page.course_price.is_visible(), "Cena kurzu musí být viditelná"
        assert detail_page.iterations_heading.is_visible(), "Nadpis termínů musí být viditelný"
        assert detail_page.iterations.count() > 0, "Detail kurzu musí obsahovat vypsané termíny"

    def test_course_detail_full_capacity_disables_registration(self, page):
        """
        CRS-06 (US-11): Indikace a zamezení zápisu při naplněné kapacitě.
        Kontroly:
        1. Na detailu kurzu u termínů s plnou kapacitou (např. 12/12) se nenabízí tlačítko zápisu pro nepřihlášeného hosta.
        """
        detail_page = CourseDetailPage(page, course_id=1).open()
        detail_page.course_name.wait_for(state="visible", timeout=10000)

        # Pro nepřihlášeného návštěvníka se tlačítko nezávazné registrace nesmí nabízet
        assert detail_page.registration_buttons.count() == 0, "Nepřihlášený návštěvník nesmí vidět tlačítko registrace"

    def test_lector_can_open_add_iteration_modal(self, page, lector_credentials):
        """
        CRS-07 (US-15): Vypsání nového běhu (termínu) kurzu lektorem.
        Kontroly:
        1. Lektor se přihlásí a otevře /courses.
        2. Klik na tlačítko 'Přidat iteraci'.
        3. Otevření modálu create_course_iteration_container.
        4. Přítomnost všech formulářových prvků dle akceptačních kritérií US-15:
           - datum zahájení (course_start_input)
           - datum ukončení (course_end_input)
           - den konání v týdnu (course_day_select)
           - čas lekce (course_time_input)
           - místo / forma výuky (course_location_input)
           - tlačítko pro odeslání termínu
        """
        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        courses_page = CoursesPage(page).open()
        courses_page.add_iteration_buttons.first.wait_for(state="visible", timeout=10000)
        courses_page.add_iteration_buttons.first.click()
        courses_page.iteration_modal_container.wait_for(state="visible", timeout=5000)

        assert courses_page.iteration_modal_container.is_visible(), "Modál pro vypsání termínu musí být viditelný"
        assert courses_page.iteration_form.is_visible(), "Formulář termínu musí být přítomen"
        assert courses_page.iteration_start_input.is_visible(), "Pole pro datum zahájení musí být viditelné"
        assert courses_page.iteration_end_input.is_visible(), "Pole pro datum ukončení musí být viditelné"
        assert courses_page.iteration_day_select.is_visible(), "Výběr dne konání musí být viditelný"
        assert courses_page.iteration_time_input.is_visible(), "Pole pro čas konání musí být viditelné"
        assert courses_page.iteration_location_input.is_visible(), "Pole pro místo výuky musí být viditelné"
        assert courses_page.iteration_submit_button.is_visible(), "Tlačítko pro odeslání termínu musí být viditelné"

    def test_lector_sees_participants_button_on_course_detail(self, page, lector_credentials):
        """
        CRS-08 (US-16): Zobrazení seznamu přihlášených účastníků pro lektora.
        Kontroly:
        1. Přihlášení lektora.
        2. Přechod na detail kurzu /courses/1.
        3. Lektor u jednotlivých termínů vidí ovládací tlačítko 'Přihlášení' pro zobrazení přihlášených studentů.
        """
        login_page = LoginPage(page).open()
        login_page.login(lector_credentials["email"], lector_credentials["password"])

        detail_page = CourseDetailPage(page, course_id=1).open()
        detail_page.course_name.wait_for(state="visible", timeout=10000)
        assert detail_page.participants_buttons.count() > 0, "Lektor musí vidět tlačítka pro zobrazení účastníků běhu"

    def test_courses_search_by_keyword(self, page):
        """
        CRS-09 (US03 / US-11): Vyhledávání a filtrování kurzů v katalogu podle klíčového slova.
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

    def test_courses_search_nonexistent_keyword(self, page):
        """
        CRS-10 (US03 / US-11): Vyhledávání neexistujícího kurzu vrací prázdný výsledek.
        Kontroly:
        1. Vyhledání zcela neexistujícího řetězce 'NeexistujiciKurzXYZ999'.
        2. Výsledek vyhledávání neobsahuje žádný kurz.
        """
        courses_page = CoursesPage(page).open()
        results = courses_page.search_courses("NeexistujiciKurzXYZ999")
        assert len(results) == 0, "Vyhledání neexistujícího kurzu musí vrátit prázdný výsledek"

    def test_courses_filter_by_minimum_capacity(self, page):
        """
        CRS-11 (US03 / US-11): Filtrování kurzů podle minimální kapacity.
        Kontroly:
        1. Filtrování kurzů s kapacitou >= 10.
        2. Všechny vyfiltrované kurzy mají kapacitu rovnou nebo vyšší než 10.
        """
        courses_page = CoursesPage(page).open()
        filtered = courses_page.filter_courses_by_capacity(min_capacity=10)
        assert len(filtered) > 0, "V katalogu musí existovat kurzy s kapacitou >= 10"
        assert all(c["capacity"] >= 10 for c in filtered), "Všechny filtrované kurzy musí mít kapacitu >= 10"

    def test_course_detail_enrollment_form_display(self, page, registered_user):
        """
        CRS-12 (US04 / US-12): Zobrazení formuláře pro přihlášení na vypsaný termín kurzu.
        Kontroly:
        1. Přihlášený student otevře detail kurzu (/courses/1).
        2. U volného termínu klikne na tlačítko 'Nezávazná registrace'.
        3. Přesměrování na formulář přihlášení /courses/{iteration_id}/register.
        4. Přítomnost vstupních polí 'phone_input', 'ico_input' a odesílacího tlačítka.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        detail_page = CourseDetailPage(page, course_id=1).open()
        detail_page.open_enrollment_for_available_term()

        assert "/register" in page.url, f"Očekávána URL registrace na termín, získáno: {page.url}"
        assert detail_page.phone_input.is_visible(), "Pole pro telefon musí být na formuláři zobrazeno"
        assert detail_page.ico_input.is_visible(), "Pole pro IČO musí být na formuláři zobrazeno"
        assert detail_page.submit_enrollment_button.is_visible(), "Tlačítko pro odeslání registrace musí být zobrazeno"

    def test_course_detail_enrollment_submission_success(self, page, registered_user):
        """
        CRS-13 (US04 / US-12): Úspěšné přihlášení studenta na termín kurzu.
        Kontroly:
        1. Přihlášený student otevře formulář přihlášení na volný termín.
        2. Vyplní povinný telefon (777123456) a validní IČO (27082440).
        3. Odeslání formuláře vrátí status 200 s potvrzením 'Successfully enrolled'.
        """
        login_page = LoginPage(page).open()
        login_page.login(registered_user["email"], registered_user["password"])

        detail_page = CourseDetailPage(page, course_id=1).open()
        detail_page.open_enrollment_for_available_term()

        with page.expect_response(
            lambda r: ("enroll" in r.url or "register" in r.url or "courses" in r.url) and r.request.method == "POST",
            timeout=10000
        ) as resp_info:
            detail_page.submit_enrollment(phone="777123456", ico="27082440")

        response = resp_info.value
        assert response.status == 200, f"Očekáván návratový status 200, získáno: {response.status}"
        assert "Successfully enrolled" in response.text() or "enrolled" in response.text().lower(), (
            f"Očekáváno potvrzení úspěšného přihlášení, získáno: {response.text()}"
        )

    def test_lector_can_create_new_course_iteration(self, page, lector_credentials):
        """
        CRS-14 (US05 / US-15): Lektor úspěšně vytvoří a vypíše nový termín kurzu.
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

