import os

class Config:
    """Central configuration for test environment and browser settings."""

    # Base application URL
    BASE_URL: str = os.getenv("BASE_URL", "http://testovani.kitner.cz")

    # Timeouts in milliseconds
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "10000"))
    NAVIGATION_TIMEOUT: int = int(os.getenv("NAVIGATION_TIMEOUT", "15000"))

    # Browser launch configuration
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")
    VIEWPORT: dict = {"width": 1280, "height": 800}
    BROWSER_ARGS: list = ["--disable-dev-shm-usage", "--no-sandbox"]

    # Pre-existing system accounts
    LECTOR_CREDENTIALS: dict = {
        "email": os.getenv("LECTOR_EMAIL", "lector@lector.com"),
        "password": os.getenv("LECTOR_PASSWORD", "lector@lector.com")
    }

