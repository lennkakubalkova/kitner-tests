from playwright.sync_api import Page, expect

class BasePage:
    """Base class for all page objects, providing standard navigation and assertion helpers using data-test/data-testid."""
    
    BASE_URL = "http://testovani.kitner.cz"
    
    def __init__(self, page: Page):
        self.page = page
        
        # Navbar locators using data-test / data-testid
        self.navigation = page.locator('[data-test="navigation"], [data-testid="navigation"]')
        self.nav_brand = page.locator('a[data-test="navigation_home_link"], a[data-testid="navigation_home_link"]')
        self.nav_courses = page.locator('li[data-test="navigation_home_list_item"] a[data-test="courses_link"]')
        self.nav_login = page.locator('li[data-test="navigation_login_item"] a[data-test="login_link"]')
        self.nav_logout = page.locator('li[data-test="navigation_logout_item"] a[data-test="logout_button"]')
        self.nav_home = page.locator('a[data-test="home_link"], a[data-testid="home_link"]')
        self.nav_profile = page.locator('li[data-test="navigation_profile_item"] a[data-test="courses_profile"]')
        self.nav_my_courses = page.locator('a[data-test="courses_link"]:has-text("Moje kurzy")')
        
        # General error container locator
        self.error_messages = page.locator('.text-error_clr')

    def is_logged_in(self) -> bool:
        """Verifies if user is logged in by checking presence of logout link and absence of login link."""
        try:
            self.nav_logout.wait_for(state="visible", timeout=3000)
        except Exception:
            pass
        return self.nav_logout.is_visible() and not self.nav_login.is_visible()

    def is_logged_out(self) -> bool:
        """Verifies if user is in logged out state."""
        try:
            self.nav_login.wait_for(state="visible", timeout=3000)
        except Exception:
            pass
        return self.nav_login.is_visible() and not self.nav_logout.is_visible()

    def logout(self):
        """Click logout button and wait for redirect."""
        self.nav_logout.click()
        self.page.wait_for_timeout(1000)

    def get_error_texts(self) -> list[str]:
        """Returns all currently visible error message strings on the page."""
        self.page.wait_for_timeout(500)
        return [el.inner_text().strip() for el in self.error_messages.all() if el.is_visible()]
