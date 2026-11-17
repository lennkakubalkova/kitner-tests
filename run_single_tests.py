import subprocess
import time
import sys

TEST_LIST = [
    # Modul 0: Úvodní navigační rozcestník (Linktree) - US-01
    ("POR-01", "tests/test_portal.py::TestPortal::test_portal_navigation_links_present_and_valid"),
    ("POR-02", "tests/test_portal.py::TestPortal::test_portal_demo_login_link_navigates_to_courses"),

    # Modul 2 & 4: Katalog, detail, správa kurzů a běhů - US-09, US-10, US-11, US-14, US-15, US-16, US-19
    ("CRS-01", "tests/test_courses.py::TestCourses::test_courses_list_visible_for_guest"),
    ("CRS-02", "tests/test_courses.py::TestCourses::test_regular_user_cannot_access_course_management"),
    ("CRS-03", "tests/test_courses.py::TestCourses::test_lector_can_open_create_course_modal"),
    ("CRS-04", "tests/test_courses.py::TestCourses::test_lector_can_create_new_course"),
    ("CRS-05", "tests/test_courses.py::TestCourses::test_course_detail_navigation_and_info"),
    ("CRS-06", "tests/test_courses.py::TestCourses::test_course_detail_full_capacity_disables_registration"),
    ("CRS-07", "tests/test_courses.py::TestCourses::test_lector_can_open_add_iteration_modal"),
    ("CRS-08", "tests/test_courses.py::TestCourses::test_lector_sees_participants_button_on_course_detail"),
    
    # Modul 1: Autentizace a sezení - US-03, US-04, US-19
    ("LOG-01", "tests/test_login.py::TestLogin::test_login_lector_success_and_privileges"),
    ("LOG-02", "tests/test_login.py::TestLogin::test_login_registered_user_success"),
    ("LOG-03", "tests/test_login.py::TestLogin::test_login_empty_fields_validation"),
    ("LOG-04", "tests/test_login.py::TestLogin::test_login_invalid_password"),
    ("LOG-05", "tests/test_login.py::TestLogin::test_login_nonexistent_user"),
    ("LOG-06", "tests/test_login.py::TestLogin::test_logout_flow_and_session_cleared"),
    ("LOG-07", "tests/test_login.py::TestLogin::test_login_navigation_to_register"),
    ("LOG-08", "tests/test_login.py::TestLogin::test_login_case_insensitive_and_trimmed_email"),
    
    # Modul 1 & 5: Registrace zákaznického účtu a uvítání - US-02, US-17
    ("REG-01", "tests/test_registration.py::TestRegistration::test_registration_success_verifies_login_state_and_welcome"),
    ("REG-02", "tests/test_registration.py::TestRegistration::test_registration_empty_form_validation"),
    ("REG-03", "tests/test_registration.py::TestRegistration::test_registration_password_mismatch"),
    ("REG-04", "tests/test_registration.py::TestRegistration::test_registration_duplicate_email"),
    ("REG-05", "tests/test_registration.py::TestRegistration::test_registration_missing_name_only"),
    ("REG-06", "tests/test_registration.py::TestRegistration::test_registration_missing_password_only"),
    ("REG-07", "tests/test_registration.py::TestRegistration::test_registration_link_navigates_to_login"),
    ("REG-08", "tests/test_registration.py::TestRegistration::test_registration_duplicate_email_case_insensitive"),

    # Modul 1: Obnova hesla - US-05
    ("RST-01", "tests/test_forgot_password.py::test_navigation_from_login_to_forgot_password"),
    ("RST-02", "tests/test_forgot_password.py::test_forgot_password_empty_email_validation"),
    ("RST-03", "tests/test_forgot_password.py::test_forgot_password_nonexistent_email_validation"),
    ("RST-04", "tests/test_forgot_password.py::test_forgot_password_registered_user_submission"),

    # Modul 5: Uživatelský profil - US-18
    ("PRF-01", "tests/test_profile.py::TestProfile::test_profile_prefilled_with_customer_data"),
    ("PRF-02", "tests/test_profile.py::TestProfile::test_profile_update_ico_and_phone"),
    ("PRF-03", "tests/test_profile.py::TestProfile::test_profile_navigation_from_menu"),

    # Modul 3: Moje kurzy - US-13
    ("MYC-01", "tests/test_my_courses.py::TestMyCourses::test_my_courses_accessible_from_navigation"),
]

def main():
    total_count = len(TEST_LIST)
    print("=" * 75, flush=True)
    print("SPUŠTĚNÍ VŠECH TESTŮ POSTUPNĚ PO JEDNOM", flush=True)
    print(f"Celkem k provedení: {total_count} testů", flush=True)
    print("=" * 75, flush=True)

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

    print("\n" + "=" * 75, flush=True)
    print("SOUHRNNÁ TABULKA VÝSLEDKŮ TESTŮ (BĚH PO JEDNOM):", flush=True)
    print("=" * 75, flush=True)
    print(f"{'#':<4} {'ID':<8} {'Stav':<8} {'Doba':<8} {'Název testu'}")
    print("-" * 75)
    for idx, code, test_name, status, duration in results:
        print(f"{idx:<4} {code:<8} {status:<8} {duration:<8} {test_name}")
    print("-" * 75)
    passed_count = sum(1 for r in results if r[3] == "PASSED")
    print(f"Celkem: {passed_count}/{total_count} PASSED | Celkový čas: {total_duration:.2f} s")
    print("=" * 75, flush=True)

if __name__ == "__main__":
    main()
