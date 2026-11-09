import time
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(
        headless=True,
        args=["--disable-dev-shm-usage", "--no-sandbox"]
    )
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    yield page
    context.close()

@pytest.fixture(scope="session")
def lector_credentials():
    return {
        "email": "lector@lector.com",
        "password": "lector@lector.com"
    }

@pytest.fixture(scope="session")
def registered_user(browser):
    """
    Session fixture that registers a genuine new user in the application
    as requested in the task conditions, and provides their credentials.
    """
    context = browser.new_context()
    page = context.new_page()
    ts = int(time.time() * 1000)
    user_data = {
        "name": f"Tester Real {ts}",
        "email": f"tester_real_{ts}@testkitner.cz",
        "password": "ValidPassword123!"
    }
    
    page.goto("http://testovani.kitner.cz/register")
    page.wait_for_load_state("networkidle")
    page.locator('input[placeholder="Jméno"]').fill(user_data["name"])
    page.locator('input[placeholder="Email"]').fill(user_data["email"])
    page.locator('input[placeholder="Heslo"]').fill(user_data["password"])
    page.locator('input[placeholder="Heslo znovu"]').fill(user_data["password"])
    page.locator('button[type="submit"]').click()
    page.wait_for_timeout(2000)
    
    # Log out to leave user in clean state for login tests
    logout_btn = page.locator('text=Odhlásit se')
    if logout_btn.is_visible():
        logout_btn.click()
        page.wait_for_timeout(1000)
        
    context.close()
    return user_data

