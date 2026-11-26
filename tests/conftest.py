import os
import re
import pytest
from playwright.sync_api import sync_playwright
from config.config import Config
from pages.register_page import RegisterPage
from utils.helpers import generate_user_data

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Stores test outcome report on item for fixture teardown evidence inspection."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

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
def page(browser, request):
    """Creates a new isolated browser context and page for each test with automatic evidence capture on failure."""
    evidence_dir = os.environ.get("EVIDENCE_DIR", os.path.join("docs", "evidence"))
    tracing_enabled = os.environ.get("PLAYWRIGHT_TRACING", "1") == "1"

    context = browser.new_context(viewport=Config.VIEWPORT)
    if tracing_enabled:
        try:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
        except Exception:
            pass

    page = context.new_page()
    page.set_default_timeout(Config.DEFAULT_TIMEOUT)

    yield page

    # Kontrola selhání testu pro automatické uložení screenshotu a trace
    rep_call = getattr(request.node, "rep_call", None)
    rep_setup = getattr(request.node, "rep_setup", None)
    is_failed = (rep_call and rep_call.failed) or (rep_setup and rep_setup.failed)

    if is_failed:
        screenshots_dir = os.path.join(evidence_dir, "screenshots")
        traces_dir = os.path.join(evidence_dir, "traces")
        os.makedirs(screenshots_dir, exist_ok=True)
        os.makedirs(traces_dir, exist_ok=True)

        safe_name = re.sub(r"[^\w\-.]", "_", request.node.name)

        # 1. Uložení screenshotu stavu stránky při selhání
        screenshot_path = os.path.join(screenshots_dir, f"{safe_name}.png")
        try:
            page.screenshot(path=screenshot_path, full_page=True, timeout=5000)
        except Exception:
            try:
                page.screenshot(path=screenshot_path, full_page=False, timeout=3000)
            except Exception:
                pass

        # 2. Uložení Playwright trace
        if tracing_enabled:
            trace_path = os.path.join(traces_dir, f"{safe_name}.zip")
            try:
                context.tracing.stop(path=trace_path)
            except Exception:
                pass
    else:
        if tracing_enabled:
            try:
                context.tracing.stop()
            except Exception:
                pass

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
