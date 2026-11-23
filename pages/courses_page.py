from playwright.sync_api import Page
from config.config import Config
from pages.base_page import BasePage

class CoursesPage(BasePage):
    """Page Object for the Courses overview page (/courses) with full data-test/data-testid locators."""

    URL = f"{BasePage.BASE_URL}/courses"

    def __init__(self, page: Page):
        super().__init__(page)
        self.courses_section = page.locator('div[data-test="courses_section"], div[data-testid="courses_section"]')
        self.courses_title = page.locator('h1[data-test="courses_title"], h1[data-testid="courses_title"]')
        
        # Lector action buttons
        self.add_course_button = page.locator('button[data-test="registration_link"]:has-text("Přidat kurz")')
        self.add_iteration_buttons = page.locator('button[data-test="registration_link"]:has-text("Přidat iteraci")')
        
        # Course card element locators
        self.course_cards = page.locator('div[data-test^="course_"], div[data-testid^="course_"]')
        self.course_names = page.locator('h2[data-test="course_name"], h2[data-testid="course_name"]')
        self.course_capacities = page.locator('p[data-test="course_capacity"], p[data-testid="course_capacity"]')
        self.course_prices = page.locator('p[data-test="course_price"], p[data-testid="course_price"]')
        self.detail_buttons = page.locator('button[data-test="registration_link"]:has-text("Chci vidět více")')

        # Modal 'Vytvořit kurz' locators
        self.modal_container = page.locator('div[data-test="course_form_container"], div[data-testid="course_form_container"]')
        self.modal_title = page.locator('h1[data-test="create_course_title"], h1[data-testid="create_course_title"]')
        self.modal_name_input = page.locator('input[data-test="course_name_input"], input[data-testid="course_name_input"]')
        self.modal_description_input = page.locator('textarea[data-test="course_description_input"], textarea[data-testid="course_description_input"]')
        self.modal_capacity_input = page.locator('input[data-test="course_capacity_input"], input[data-testid="course_capacity_input"]')
        self.modal_price_input = page.locator('input[data-test="course_price_input"], input[data-testid="course_price_input"]')
        self.modal_submit_button = page.locator('div[data-test="course_form_submit_button_container"] button, button[data-test="registration_link"]:has-text("Vytvořit kurz")')

        # Modal 'Přidat iteraci' locators (US-15)
        self.iteration_modal_container = page.locator('div[data-test="create_course_iteration_container"]')
        self.iteration_form = page.locator('form[data-test="course_iteration_form"]')
        self.iteration_start_input = page.locator('input[data-test="course_start_input"]')
        self.iteration_end_input = page.locator('input[data-test="course_end_input"]')
        self.iteration_day_select = page.locator('select[data-test="course_day_select"]')
        self.iteration_time_input = page.locator('input[data-test="course_time_input"]')
        self.iteration_location_input = page.locator('input[data-test="course_location_input"]')
        self.iteration_submit_button = page.locator('form[data-test="course_iteration_form"] button[data-test="registration_link"]')


    def open(self):
        """Navigate to the courses page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
        return self

    def has_lector_controls(self) -> bool:
        """Returns True if lector-specific controls (add course, add iteration) are visible."""
        return self.add_course_button.is_visible() and self.add_iteration_buttons.count() > 0

    def create_course(self, name: str, description: str, capacity: int, price: int):
        """Opens modal and creates a new course."""
        self.add_course_button.click()
        self.modal_name_input.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        self.modal_name_input.fill(name)
        self.modal_description_input.fill(description)
        self.modal_capacity_input.fill(str(capacity))
        self.modal_price_input.fill(str(price))
        self.modal_submit_button.click()
        try:
            self.modal_container.wait_for(state="hidden", timeout=Config.DEFAULT_TIMEOUT)
        except Exception:
            self.page.wait_for_load_state("networkidle")

    def create_iteration(self, start_date: str, end_date: str, day_index: int = 1, time_str: str = "18:00", location: str = "Online MS Teams"):
        """Opens modal and creates a new course iteration (term) for the first course (US-15 / US05)."""
        self.add_iteration_buttons.first.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        self.add_iteration_buttons.first.click()
        self.iteration_modal_container.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        self.iteration_start_input.fill(start_date)
        self.iteration_end_input.fill(end_date)
        self.iteration_day_select.select_option(index=day_index)
        self.iteration_time_input.fill(time_str)
        self.iteration_location_input.fill(location)
        self.iteration_submit_button.click()
        try:
            self.iteration_modal_container.wait_for(state="hidden", timeout=Config.DEFAULT_TIMEOUT)
        except Exception:
            self.page.wait_for_load_state("networkidle")

    def get_all_course_names(self) -> list[str]:
        """Returns all visible course names on the page."""
        self.course_names.first.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        return [el.inner_text().strip() for el in self.course_names.all()]

    def search_courses(self, keyword: str) -> list[str]:
        """Filters/searches loaded courses matching the given keyword (US-11 / US03)."""
        names = self.get_all_course_names()
        return [name for name in names if keyword.lower() in name.lower()]

    def filter_courses_by_capacity(self, min_capacity: int) -> list[dict]:
        """Filters courses having at least min_capacity (US-11 / US03)."""
        self.course_cards.first.wait_for(state="visible", timeout=Config.DEFAULT_TIMEOUT)
        results = []
        for card in self.course_cards.all():
            cap_elem = card.locator('p[data-test="course_capacity"], p[data-testid="course_capacity"]').first
            name_elem = card.locator('h2[data-test="course_name"], h2[data-testid="course_name"]').first
            if cap_elem.is_visible() and name_elem.is_visible():
                text = cap_elem.inner_text()
                digits = [int(s) for s in text.split() if s.isdigit()]
                if digits and digits[0] >= min_capacity:
                    results.append({"name": name_elem.inner_text().strip(), "capacity": digits[0]})
        return results
