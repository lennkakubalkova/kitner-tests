from playwright.sync_api import Page, expect

class BasePage:
    """Base class for all page objects, providing common navigation and assertion helpers."""
    
    BASE_URL = "http://testovani.kitner.cz"
    
    def __init__(self, page: Page):
        self.page = page
        
        # Navbar locators
        self.nav_brand = page.locator("nav a").first
        self.nav_courses = page.locator('nav a:has-text("Kurzy"), nav a:has-text("Přehled kurzů")')
        self.nav_login = page.locator('nav a:has-text("Přihlásit se")')
        self.nav_logout = page.locator('nav a:has-text("Odhlásit se"), a:has-text("Odhlásit se")')
        self.nav_home = page.locator('nav a:has-text("Domů")')
        self.nav_my_courses = page.locator('nav a:has-text("Moje kurzy")')
        self.nav_profile = page.locator('nav a:has-text("Můj Profil")')
        
        # General error container locator
        self.error_messages = page.locator('.text-error_clr')

    def is_logged_in(self) -> bool:
        """Verifies if user is logged in by checking presence of logout link and absence of login link."""
        logout_visible = self.nav_logout.is_visible()
        login_visible = self.nav_login.is_visible()
        return logout_visible and not login_visible

    def is_logged_out(self) -> bool:
        """Verifies if user is in logged out state."""
        return self.nav_login.is_visible() and not self.nav_logout.is_visible()

    def logout(self):
        """Click logout button and wait for redirect."""
        self.nav_logout.click()
        self.page.wait_for_timeout(1000)

    def get_error_texts(self) -> list[str]:
        """Returns all currently visible error message strings on the page."""
        self.page.wait_for_timeout(500)
        return [el.inner_text().strip() for el in self.error_messages.all() if el.is_visible()]

