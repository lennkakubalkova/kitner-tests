#!/usr/bin/env python3
"""
Skript: verify_testcases.py
Účel: Skript "Definice hotovo" pro skill ust-to-tc.
Kontroluje, zda vytvořené manuální test casy splňují všechny kvalitativní požadavky:
1. Každé deklarované akceptační kritérium (AC) má přiřazen alespoň jeden test case.
2. Každý test case obsahuje: ID, název, předpoklady, kroky a očekávaný výsledek.
3. V dokumentu nezůstaly žádné nedokončené položky (TODO, TBD, ???, [Doplňte]).
"""

import sys
import re
import os

def verify_testcases_file(filepath: str) -> bool:
    if not os.path.exists(filepath):
        print(f"[CHYBA] Soubor neexistuje: {filepath}")
        return False

    content = None
    for enc in ("utf-8", "utf-8-sig", "cp1250", "windows-1250", "latin1"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        print(f"[CHYBA] Nepodařilo se dekódovat soubor: {filepath}")
        return False

    errors = []
    warnings = []
    
    print("=" * 70)
    print(f"KONTROLA DEFINICE HOTOVO (DoD) PRO SOUBOR: {os.path.basename(filepath)}")
    print("=" * 70)

    # 1. Hledání akceptačních kritérií (AC)
    # Hledáme AC1, AC2, AC-1, AC_1 apod.
    ac_matches = set(re.findall(r"\bAC[-_]?(\d+)\b", content, re.IGNORECASE))
    if not ac_matches:
        warnings.append("V textu nebyla nalezena explicitní akceptační kritéria ve formátu AC1, AC2 apod.")
        declared_acs = set()
    else:
        declared_acs = {f"AC{num}" for num in ac_matches}
        print(f"[OK] Nalezena akceptační kritéria: {', '.join(sorted(declared_acs, key=lambda x: int(re.search(r'\d+', x).group())))}")

    # 2. Hledání Test Casů
    # Hledáme nadpisy typu ### TC-01: ... nebo ### TC_01: ... nebo ## TC-1: ...
    tc_blocks = re.split(r"(?m)^#{2,4}\s+(TC[-_]?[0-9A-Za-z]+.*?)$", content)
    
    # První element je text před prvním TC
    header_section = tc_blocks[0]
    tc_items = []
    for i in range(1, len(tc_blocks), 2):
        tc_title = tc_blocks[i].strip()
        tc_body = tc_blocks[i+1].strip() if i+1 < len(tc_blocks) else ""
        tc_items.append((tc_title, tc_body))

    if not tc_items:
        errors.append("V dokumentu nebyl nalezen žádný test case začínající na '### TC-...'!")
        print(f"[CHYBA] Nalezeno test casů: 0")
    else:
        print(f"[OK] Nalezeno celkem test casů: {len(tc_items)}")

    # 3. Kontrola každého Test Casu
    covered_acs = set()

    for idx, (title, body) in enumerate(tc_items, start=1):
        tc_name = title.split("\n")[0]
        
        # Kontrola vazby na AC
        ac_in_tc = re.findall(r"\bAC[-_]?(\d+)\b", body, re.IGNORECASE)
        if ac_in_tc:
            for num in ac_in_tc:
                covered_acs.add(f"AC{num}")
        else:
            errors.append(f"[{tc_name}] Chybí vazba na akceptační kritérium (např. * **Pokrytá kritéria:** AC1)")

        # Kontrola předpokladů (Preconditions)
        if not re.search(r"(?i)(předpoklady|preconditions)", body):
            errors.append(f"[{tc_name}] Chybí sekce předpokladů (Předpoklady / Preconditions)!")
        
        # Kontrola kroků (Steps)
        if not re.search(r"(?i)(kroky|steps)", body) or not re.search(r"\d+\.\s+", body):
            errors.append(f"[{tc_name}] Chybí číslované testovací kroky (1. ..., 2. ...)!")

        # Kontrola očekávaného výsledku (Expected result)
        if not re.search(r"(?i)(očekávaný výsledek|expected result)", body):
            errors.append(f"[{tc_name}] Chybí jednoznačný očekávaný výsledek (Očekávaný výsledek / Expected Result)!")

    # 4. Kontrola 100% pokrytí všech deklarovaných AC
    if declared_acs:
        uncovered_acs = declared_acs - covered_acs
        if uncovered_acs:
            errors.append(f"Následující akceptační kritéria nemají žádný test case: {', '.join(sorted(uncovered_acs))}")
        else:
            print(f"[OK] Všechna akceptační kritéria ({len(declared_acs)}) mají přiřazen alespoň jeden test case.")

    # 5. Kontrola zakázaných textů (TODO, TBD, ???)
    forbidden_patterns = [r"\bTODO\b", r"\bTBD\b", r"\?\?\?", r"\[Doplňte\]", r"\[Chybí\]"]
    for pattern in forbidden_patterns:
        found = re.findall(pattern, content, re.IGNORECASE)
        if found:
            errors.append(f"V dokumentu byl nalezen nedokončený text: '{found[0]}'")

    print("-" * 70)
    
    # Výpis varování
    for w in warnings:
        print(f"[VAROVÁNÍ] {w}")

    # Výpis chyb a vyhodnocení
    if errors:
        print("\nNALEZENY NÁSLEDUJÍCÍ NESHODY S DEFINICÍ HOTOVO:")
        for e in errors:
            print(f"  ❌ {e}")
        print("\n" + "=" * 70)
        print("VÝSLEDEK KONTROLY: ❌ FAIL (dokument nesplňuje požadavky)")
        print("=" * 70)
        return False
    else:
        print("\n" + "=" * 70)
        print("VÝSLEDEK KONTROLY: ✅ PASS (všechna kritéria definice hotovo splněna!)")
        print("=" * 70)
        return True

def main():
    if len(sys.argv) < 2:
        print("Použití: python verify_testcases.py <cesta_k_souboru_s_testy.md>")
        sys.exit(1)

    target_file = sys.argv[1]
    success = verify_testcases_file(target_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
