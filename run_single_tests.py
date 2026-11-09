import subprocess
import time
import sys

TEST_LIST = [
    # Courses
    ("CRS-01", "tests/test_courses.py::TestCourses::test_courses_list_visible_for_guest"),
    ("CRS-02", "tests/test_courses.py::TestCourses::test_regular_user_cannot_access_course_management"),
    ("CRS-03", "tests/test_courses.py::TestCourses::test_lector_can_open_create_course_modal"),
    ("CRS-04", "tests/test_courses.py::TestCourses::test_lector_can_create_new_course"),
    
    # Login & Session
    ("LOG-01", "tests/test_login.py::TestLogin::test_login_lector_success_and_privileges"),
    ("LOG-02", "tests/test_login.py::TestLogin::test_login_registered_user_success"),
    ("LOG-03", "tests/test_login.py::TestLogin::test_login_empty_fields_validation"),
    ("LOG-04", "tests/test_login.py::TestLogin::test_login_invalid_password"),
    ("LOG-05", "tests/test_login.py::TestLogin::test_login_nonexistent_user"),
    ("LOG-06", "tests/test_login.py::TestLogin::test_logout_flow_and_session_cleared"),
    ("LOG-07", "tests/test_login.py::TestLogin::test_login_navigation_to_register"),
    
    # Registration
    ("REG-01", "tests/test_registration.py::TestRegistration::test_registration_success_verifies_login_state_and_welcome"),
    ("REG-02", "tests/test_registration.py::TestRegistration::test_registration_empty_form_validation"),
    ("REG-03", "tests/test_registration.py::TestRegistration::test_registration_password_mismatch"),
    ("REG-04", "tests/test_registration.py::TestRegistration::test_registration_duplicate_email"),
    ("REG-05", "tests/test_registration.py::TestRegistration::test_registration_missing_name_only"),
    ("REG-06", "tests/test_registration.py::TestRegistration::test_registration_missing_password_only"),
    ("REG-07", "tests/test_registration.py::TestRegistration::test_registration_link_navigates_to_login"),

    # Forgot Password (Obnova hesla)
    ("RST-01", "tests/test_forgot_password.py::test_navigation_from_login_to_forgot_password"),
    ("RST-02", "tests/test_forgot_password.py::test_forgot_password_empty_email_validation"),
    ("RST-03", "tests/test_forgot_password.py::test_forgot_password_nonexistent_email_validation"),
    ("RST-04", "tests/test_forgot_password.py::test_forgot_password_registered_user_submission"),
]

def main():
    total_count = len(TEST_LIST)
    print("=" * 70, flush=True)
    print("SPUŠTĚNÍ VŠECH TESTŮ POSTUPNĚ PO JEDNOM", flush=True)
    print(f"Celkem k provedení: {total_count} testů", flush=True)
    print("=" * 70, flush=True)

    results = []
    total_start = time.time()

    for idx, (code, test_node) in enumerate(TEST_LIST, start=1):
        test_name = test_node.split("::")[-1]
        print(f"\n[{idx:02d}/{total_count}] Spouštím: {code} -> {test_name} ...", end=" ", flush=True)
        
        t0 = time.time()
        res = subprocess.run(
            ["py", "-m", "pytest", test_node, "-q", "--tb=line"],
            capture_output=True,
            text=True
        )
        duration = time.time() - t0
        
        status = "PASSED" if res.returncode == 0 else "FAILED"
        print(f"[{status}] za {duration:.2f} s", flush=True)
        results.append((idx, code, test_name, status, f"{duration:.2f}s"))

    total_duration = time.time() - total_start

    print("\n" + "=" * 70, flush=True)
    print("SOUHRNNÁ TABULKA VÝSLEDKŮ TESTŮ (BĚH PO JEDNOM):", flush=True)
    print("=" * 70, flush=True)
    print(f"{'#':<4} {'ID':<8} {'Stav':<8} {'Doba':<8} {'Název testu'}")
    print("-" * 70)
    for idx, code, test_name, status, duration in results:
        print(f"{idx:<4} {code:<8} {status:<8} {duration:<8} {test_name}")
    print("-" * 70)
    passed_count = sum(1 for r in results if r[3] == "PASSED")
    print(f"Celkem: {passed_count}/{total_count} PASSED | Celkový čas: {total_duration:.2f} s")
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
