import pytest
from playwright.sync_api import sync_playwright
from config.config import Config
from pages.register_page import RegisterPage
from utils.helpers import generate_user_data

@pytest.fixture(scope="session")
def playwright_instance():
    """Initializes Playwright runtime for the test session."""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    """Launches the shared browser instance using central configuration."""
    browser = playwright_instance.chromium.launch(
        headless=Config.HEADLESS,
        args=Config.BROWSER_ARGS
    )
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def page(browser):
    """Creates a new isolated browser context and page for each test."""
    context = browser.new_context(viewport=Config.VIEWPORT)
    page = context.new_page()
    page.set_default_timeout(Config.DEFAULT_TIMEOUT)
    yield page
    context.close()

@pytest.fixture(scope="session")
def lector_credentials():
    """Returns official lector credentials from central configuration."""
    return Config.LECTOR_CREDENTIALS

@pytest.fixture(scope="session")
def registered_user(browser):
    """
    Session fixture creating a genuine registered user in the application.
    Uses RegisterPage with standard data-test / data-testid locators:
      - input[data-test="name_input"]
      - input[data-test="email_input"]
      - input[data-test="password_input"]
      - input[data-test="password_again_input"]
      - button[data-test="register_button"]
    """
    context = browser.new_context(viewport=Config.VIEWPORT)
    page = context.new_page()
    page.set_default_timeout(Config.DEFAULT_TIMEOUT)

    user_data = generate_user_data(name_prefix="Tester Real")

    # Registrace přes Page Object Model RegisterPage s data-test selektory
    reg_page = RegisterPage(page).open()
    reg_page.register(
        name=user_data["name"],
        email=user_data["email"],
        password=user_data["password"],
        password_confirmation=user_data["password_confirmation"]
    )

    # Ověření úspěšné registrace a čisté odhlášení před spuštěním testů
    assert reg_page.is_logged_in(), f"Uživatel {user_data['email']} nebyl po registraci úspěšně přihlášen"
    reg_page.logout()
    assert reg_page.is_logged_out(), "Uživatel nebyl po registraci úspěšně odhlášen"

    context.close()
    return user_data
