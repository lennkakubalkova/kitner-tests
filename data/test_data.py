class ErrorMessages:
    """Expected validation and error messages across all modules."""
    REQUIRED_NAME = "The name field is required."
    REQUIRED_EMAIL = "The email field is required."
    REQUIRED_PASSWORD = "The password field is required."
    PASSWORD_CONFIRMATION_MISMATCH = "The password field confirmation does not match."
    EMAIL_ALREADY_TAKEN = "The email has already been taken."
    INVALID_CREDENTIALS = "These credentials do not match our records."
    USER_NOT_FOUND = "We can't find a user with that email address."
    RATE_LIMIT_WAIT = "Please wait before retrying."


class StatusMessages:
    """Expected success and status notification messages."""
    RESET_PASSWORD_SUCCESS = "We have emailed your password reset link."


class UserData:
    """Static and template user data for testing."""
    DEFAULT_PASSWORD = "ValidPassword123!"
    INVALID_PASSWORD = "ZcelaSpatneHeslo999!"
    NONEXISTENT_EMAIL_PREFIX = "nonexistent_qa_user"


class CourseData:
    """Templates for course management testing."""
    DEFAULT_TITLE_PREFIX = "QA Kurz"
    DEFAULT_DESCRIPTION = "Komplexni kurz automatizace testovani s Playwright a pytest."
    DEFAULT_CAPACITY = 16
    DEFAULT_PRICE = 3990


class ProfileData:
    """Test data for customer profile module (US-18)."""
    VALID_ICO = "27082440"  # Valid Czech IČO with modulo 11 weighted checksum
    INVALID_ICO = "12345678"
    VALID_PHONE = "777123456"


class LogoutData:
    """Test data and expectations for user logout scenarios."""
    LOGOUT_SUCCESS_URL_KEYWORD = "login"
    EXPECTED_LOGIN_BUTTON_TEXT = "Přihlásit se"


