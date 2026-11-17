import time
import random
from data.test_data import UserData, CourseData

def generate_unique_email(prefix: str = "qa_user") -> str:
    """Generate a unique timestamped email address for registration testing."""
    ts = int(time.time() * 1000)
    rand = random.randint(100, 999)
    return f"{prefix}_{ts}_{rand}@testkitner.cz"

def generate_user_data(name_prefix: str = "Tester Real") -> dict:
    """Generate a full test user dictionary for genuine application registration."""
    ts = int(time.time() * 1000)
    return {
        "name": f"{name_prefix} {ts}",
        "email": generate_unique_email(prefix="student"),
        "password": UserData.DEFAULT_PASSWORD,
        "password_confirmation": UserData.DEFAULT_PASSWORD
    }

def generate_course_data(title_prefix: str = CourseData.DEFAULT_TITLE_PREFIX) -> dict:
    """Generate course creation payload with unique title."""
    ts = int(time.time())
    rand = random.randint(10, 99)
    return {
        "name": f"{title_prefix} {ts}_{rand}",
        "description": CourseData.DEFAULT_DESCRIPTION,
        "capacity": CourseData.DEFAULT_CAPACITY,
        "price": CourseData.DEFAULT_PRICE
    }

def validate_ico_checksum(ico: str) -> bool:
    """
    Validates Czech IČO (Identifikační číslo osoby) using weighted sum modulo 11 algorithm.
    Official algorithm used in US-12 and US-18.
    """
    if not ico or not ico.isdigit() or len(ico) != 8:
        return False
    weights = [8, 7, 6, 5, 4, 3, 2]
    total = sum(int(ico[i]) * weights[i] for i in range(7))
    remainder = total % 11
    if remainder == 0:
        check_digit = 1
    elif remainder == 1:
        check_digit = 0
    else:
        check_digit = 11 - remainder
    return int(ico[7]) == check_digit

