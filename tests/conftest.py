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
    Session fixture that registers a genuine new user in the application
    using the Page Object Model (RegisterPage) and genuine form submission.
    """
    context = browser.new_context(viewport=Config.VIEWPORT)
    page = context.new_page()
    user_data = generate_user_data(name_prefix="Tester Real")

    reg_page = RegisterPage(page).open()
    reg_page.register(
        name=user_data["name"],
        email=user_data["email"],
        password=user_data["password"],
        password_confirmation=user_data["password_confirmation"]
    )

    # Log out to leave user in clean state for subsequent tests
    if reg_page.is_logged_in():
        reg_page.logout()

    context.close()
    return user_data
