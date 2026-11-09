from playwright.sync_api import Page
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
        self.page.wait_for_timeout(1000)
        self.modal_name_input.fill(name)
        self.modal_description_input.fill(description)
        self.modal_capacity_input.fill(str(capacity))
        self.modal_price_input.fill(str(price))
        self.modal_submit_button.click()
        self.page.wait_for_timeout(2000)
