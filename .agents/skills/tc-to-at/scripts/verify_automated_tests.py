#!/usr/bin/env python3
"""
Skript: verify_automated_tests.py
Účel: Skript "Definice hotovo" pro skill tc-to-at.
Kontroluje, zda vytvořené automatizované testy splňují všechny kvalitativní a architektonické požadavky:
1. Každý manuální test case (TC-xx) má odpovídající automatizovaný test.
2. V testech nejsou žádná pevná čekání (time.sleep, wait_for_timeout).
3. V testovacích souborech nejsou žádné přímé selektory (page.locator, page.get_by_*).
4. V testech není žádná simulace odpovědí serveru (page.route).
5. Stabilita: Testy jsou spuštěny 3× po sobě a všechny běhy musí skončit 100% zelené.
"""

import sys
import os
import re
import argparse
import subprocess
import time

def read_file_safe(filepath: str) -> str:
    """Reads a text file with multiple encoding fallbacks."""
    for enc in ("utf-8", "utf-8-sig", "cp1250", "windows-1250", "latin1"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""

def get_python_executable() -> str:
    """Finds the appropriate Python executable (preferring venv if active)."""
    # Check current workspace .venv
    candidate_venv = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    if os.path.exists(candidate_venv):
        return candidate_venv
    
    # Check scratch .venv
    scratch_venv = r"c:\Users\Jan\.gemini\antigravity\scratch\kitner-tests\.venv\Scripts\python.exe"
    if os.path.exists(scratch_venv):
        return scratch_venv
        
    return sys.executable

def verify_automated_tests(tc_file: str, test_file: str, runs: int = 3) -> bool:
    print("=" * 75)
    print("KONTROLA DEFINICE HOTOVO (DoD) PRO AUTOMATIZOVANÉ TESTY")
    print("=" * 75)
    print(f"Manuální test casy: {tc_file}")
    print(f"Automatizovaný test: {test_file}")
    print(f"Počet ověřovacích běhů: {runs}")
    print("-" * 75)

    errors = []

    # 1. Kontrola existence souborů
    if not os.path.exists(tc_file):
        print(f"[CHYBA] Soubor manuálních testů neexistuje: {tc_file}")
        return False
    if not os.path.exists(test_file):
        print(f"[CHYBA] Soubor automatizovaných testů neexistuje: {test_file}")
        return False

    tc_content = read_file_safe(tc_file)
    test_content = read_file_safe(test_file)

    # 2. Kontrola pokrytí manuálních TC (TC-xx)
    tc_matches = sorted(list(set(re.findall(r"\bTC[-_]?(\d+)\b", tc_content, re.IGNORECASE))))
    if not tc_matches:
        print("[VAROVÁNÍ] V manuálním souboru nebyla nalezena žádná ID typu TC-01.")
    else:
        print(f"1. KONTROLA POKRYTÍ MANUÁLNÍCH TESTŮ ({len(tc_matches)} nalezeno):")
        uncovered = []
        for tc_num in tc_matches:
            # Hledáme např. TC-01, TC_01, tc01 apod. v kódu nebo docstringu
            pattern = rf"\bTC[-_]?{tc_num}\b"
            if re.search(pattern, test_content, re.IGNORECASE):
                print(f"   [OK] TC-{tc_num:02} je pokryt v testovacím souboru.")
            else:
                uncovered.append(f"TC-{tc_num:02}")
                print(f"   [CHYBA] TC-{tc_num:02} NENÍ nalezen v testovacím souboru!")
        
        if uncovered:
            errors.append(f"Nenalezeny automatizované testy pro manuální scénáře: {', '.join(uncovered)}")

    # 3. Statická analýza kódu a dodržení pravidel projektu
    print("\n2. STATICKÁ ANALÝZA KÓDU (Pravidla projektu z AGENTS.md):")
    
    # Pravidlo 1: Žádné time.sleep
    if re.search(r"\btime\.sleep\(", test_content):
        errors.append("V testovacím souboru bylo nalezeno zakázané pevné čekání 'time.sleep()'!")
        print("   ❌ time.sleep() NALEZENO")
    else:
        print("   [OK] Žádný výskyt time.sleep()")

    # Pravidlo 2: Žádné wait_for_timeout
    if re.search(r"\.wait_for_timeout\(", test_content):
        errors.append("V testovacím souboru bylo nalezeno zakázané pevné čekání 'wait_for_timeout()'!")
        print("   ❌ wait_for_timeout() NALEZENO")
    else:
        print("   [OK] Žádný výskyt wait_for_timeout()")

    # Pravidlo 3: Žádné přímé lokátory v testech
    direct_locators = re.findall(r"page\.(locator|get_by_\w+)\(", test_content)
    if direct_locators:
        errors.append(f"V testovacím souboru byly nalezeny přímé lokátory ({set(direct_locators)})! Všechny selektory musí být v Page Objectu.")
        print(f"   ❌ Přímé lokátory nalezeny: {set(direct_locators)}")
    else:
        print("   [OK] Žádné přímé lokátory v testovacím souboru (pouze Page Objecty)")

    # Pravidlo 4: Zákaz simulace odpovědí serveru
    if re.search(r"page\.route\(", test_content):
        errors.append("V testovacím souboru bylo nalezeno zakázané mockování 'page.route()'! Testy musí volat reálné prostředí.")
        print("   ❌ page.route() NALEZENO")
    else:
        print("   [OK] Žádná simulace odpovědí serveru (reálné testování)")

    if errors:
        print("\n" + "=" * 75)
        print("KONTROLA DEFINICE HOTOVO SELHALA NA STATICKÝCH PRAVIDLECH:")
        for e in errors:
            print(f"  ❌ {e}")
        print("=" * 75)
        return False

    # 4. Stabilita testů (Ověření 3× zeleného běhu)
    print(f"\n3. STABILITA TESTŮ (Ověření {runs}× po sobě jdoucích úspěšných běhů):")
    python_exe = get_python_executable()
    
    for run_idx in range(1, runs + 1):
        print(f"   Běh {run_idx}/{runs}: Spouštím pytest {test_file} ...", end=" ", flush=True)
        t0 = time.time()
        
        cmd = [python_exe, "-m", "pytest", test_file, "-q", "--tb=line"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        duration = time.time() - t0
        
        if res.returncode == 0:
            print(f"✅ PASSED ({duration:.2f} s)")
        else:
            print(f"❌ FAILED ({duration:.2f} s)")
            print("\nChyba z běhu testu:")
            print(res.stdout or res.stderr)
            errors.append(f"Běh č. {run_idx} selhal s chybou v testech!")
            break

    print("-" * 75)
    if errors:
        print("\nVÝSLEDEK DEFINICE HOTOVO: ❌ FAIL")
        for e in errors:
            print(f"  ❌ {e}")
        print("=" * 75)
        return False
    else:
        print("\nVÝSLEDEK DEFINICE HOTOVO: ✅ PASS")
        print("Všechny požadavky kvality, pokrytí a stability byly 100% splněny.")
        print("=" * 75)
        return True

def main():
    parser = argparse.ArgumentParser(description="Ověření Definice hotovo (DoD) pro automatizované testy.")
    parser.add_argument("--tc-file", required=True, help="Cesta k souboru s manuálními test casy (.md)")
    parser.add_argument("--test-file", required=True, help="Cesta k souboru s automatizovaným testem (.py)")
    parser.add_argument("--runs", type=int, default=3, help="Počet ověřovacích běhů testů (výchozí: 3)")

    args = parser.parse_args()
    success = verify_automated_tests(args.tc_file, args.test_file, args.runs)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
