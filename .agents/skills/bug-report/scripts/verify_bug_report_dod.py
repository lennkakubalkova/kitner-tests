#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_bug_report_dod.py
------------------------
Stop hook pro Antigravity Agent:
Vynucuje Definici hotovo (Definition of Done) pro reportování chyb:
Nepustí agenta skončit, dokud:
1. Existuje HTML přehled (docs/bug_report.html).
2. Je v něm report pro každý padající test.
3. Každý report má všechna povinná pole:
   - kroky k reprodukci,
   - očekávaný výsledek,
   - skutečný výsledek,
   - prostředí,
   - odkaz na důkaz (screenshot nebo trace z testu).

Používá výhradně standardní knihovnu Pythonu (žádné externí závislosti).
Vstup: JSON na stdin (kontext hooku).
Výstup: JSON na stdout: {"decision": "allow"} nebo {"decision": "continue", "reason": "..."}.
"""

import os
import sys
import re
import json
import threading
import xml.etree.ElementTree as ET


def read_stdin_with_timeout(timeout_sec: float = 0.5) -> dict:
    """Bezpečně přečte JSON z stdin s timeoutem pro prevenci zablokování."""
    hook_input = {}
    raw_text = []

    def _reader():
        try:
            content = sys.stdin.read()
            raw_text.append(content)
        except Exception:
            pass

    t = threading.Thread(target=_reader)
    t.daemon = True
    t.start()
    t.join(timeout_sec)

    if raw_text and raw_text[0].strip():
        try:
            hook_input = json.loads(raw_text[0])
        except Exception:
            pass

    return hook_input


def find_project_root(hook_input: dict) -> str:
    """Určí kořenový adresář projektu z kontextu hooku nebo z CWD."""
    # 1. Z workspacePaths v kontextu
    ws_paths = hook_input.get("workspacePaths", [])
    if ws_paths and os.path.exists(ws_paths[0]):
        return os.path.abspath(ws_paths[0])

    # 2. Z cwd v kontextu
    cwd = hook_input.get("cwd")
    if cwd and os.path.exists(cwd):
        return os.path.abspath(cwd)

    # 3. Z aktuálního pracovního adresáře
    curr = os.path.abspath(os.getcwd())
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, "pytest.ini")) or os.path.exists(os.path.join(curr, ".git")):
            return curr
        curr = os.path.dirname(curr)

    return os.path.abspath(os.getcwd())


def get_failing_tests_from_junit(project_root: str) -> list[dict]:
    """Získá seznam padajících testů z posledního JUnit XML reportu."""
    junit_candidates = [
        os.path.join(project_root, "reports", "junit_temp_report.xml"),
        os.path.join(project_root, "reports", "junit_report.xml"),
    ]

    for jpath in junit_candidates:
        if os.path.exists(jpath):
            try:
                tree = ET.parse(jpath)
                root = tree.getroot()
                suites = root.findall(".//testsuite") if root.tag != "testsuite" else [root]
                failing = []
                for suite in suites:
                    for tc in suite.findall("testcase"):
                        fail = tc.find("failure")
                        err = tc.find("error")
                        if fail is not None or err is not None:
                            name = tc.attrib.get("name", "")
                            classname = tc.attrib.get("classname", "")
                            clean_name = name.split("[")[0]
                            failing.append({
                                "name": name,
                                "clean_name": clean_name,
                                "classname": classname,
                                "message": (fail if fail is not None else err).attrib.get("message", "")
                            })
                return failing
            except Exception:
                pass

    return []


def validate_defect_card(card_html: str, project_root: str, html_dir: str) -> list[str]:
    """
    Ověří přítomnost všech povinných polí v kartě vady:
    - kroky k reprodukci
    - očekávaný výsledek
    - skutečný výsledek
    - prostředí
    - odkaz na důkaz (screenshot nebo trace z testu s existujícím souborem)
    """
    missing = []

    # 1. Kroky k reprodukci
    has_steps = False
    repro_match = re.search(r'<ol[^>]*class="[^"]*repro-steps[^"]*"[^>]*>(.*?)</ol>', card_html, re.DOTALL)
    if repro_match and "<li>" in repro_match.group(1):
        has_steps = True
    elif "Kroky k reprodukci" in card_html and "<li" in card_html:
        has_steps = True
    if not has_steps:
        missing.append("Kroky k reprodukci (repro-steps)")

    # 2. Očekávaný výsledek
    has_expected = False
    exp_match = re.search(r'class="[^"]*expected-box[^"]*"[^>]*>.*?<p>(.*?)</p>', card_html, re.DOTALL)
    if exp_match and exp_match.group(1).strip():
        has_expected = True
    elif "Očekávaný výsledek" in card_html:
        has_expected = True
    if not has_expected:
        missing.append("Očekávaný výsledek (expected result)")

    # 3. Skutečný výsledek
    has_actual = False
    act_match = re.search(r'class="[^"]*actual-box[^"]*"[^>]*>.*?<p>(.*?)</p>', card_html, re.DOTALL)
    if act_match and act_match.group(1).strip():
        has_actual = True
    elif "Skutečný výsledek" in card_html:
        has_actual = True
    if not has_actual:
        missing.append("Skutečný výsledek (actual result)")

    # 4. Odkaz na důkaz (Screenshot nebo Trace) a ověření existence souboru na disku
    has_evidence = False
    evidence_found = []

    # Screenshot kontrola
    scr_matches = re.findall(r'<a\s+[^>]*href=["\']([^"\']+\.png)["\']', card_html, re.IGNORECASE)
    for scr in scr_matches:
        abs_scr = os.path.normpath(os.path.join(html_dir, scr)) if not os.path.isabs(scr) else scr
        if os.path.exists(abs_scr):
            has_evidence = True
            evidence_found.append(f"Screenshot: {os.path.basename(abs_scr)}")

    # Trace kontrola
    trc_matches = re.findall(r'<a\s+[^>]*href=["\']([^"\']+\.zip)["\']', card_html, re.IGNORECASE)
    for trc in trc_matches:
        abs_trc = os.path.normpath(os.path.join(html_dir, trc)) if not os.path.isabs(trc) else trc
        if os.path.exists(abs_trc):
            has_evidence = True
            evidence_found.append(f"Trace: {os.path.basename(abs_trc)}")

    if not has_evidence:
        missing.append("Odkaz na existující důkaz (screenshot .png nebo trace .zip soubor)")

    return missing


def verify_definition_of_done(project_root: str) -> tuple[bool, list[str]]:
    """
    Vyhodnotí všechny 3 podmínky Definice hotovo:
    1. existuje HTML přehled (docs/bug_report.html),
    2. je v něm report pro každý padající test,
    3. každý report má všechna povinná pole.
    """
    issues = []

    html_path = os.path.join(project_root, "docs", "bug_report.html")
    html_dir = os.path.dirname(html_path)

    # Podmínka 1: Existuje HTML přehled
    if not os.path.exists(html_path):
        issues.append(f"HTML přehled chyb neexistuje na očekávané cestě: '{os.path.relpath(html_path, project_root)}'.")
        return False, issues

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        issues.append(f"Nelze přečíst HTML přehled '{html_path}': {e}")
        return False, issues

    if len(html_content.strip()) < 100:
        issues.append(f"HTML přehled '{html_path}' je prázdný nebo nekompletní.")
        return False, issues

    # Kontrola globálního pole: Testovací prostředí
    has_environment = bool(re.search(r'class="[^"]*env-tag[^"]*"', html_content) or "Prostředí:" in html_content)
    if not has_environment:
        issues.append("V HTML přehledu chybí specifikace testovacího prostředí (OS, prohlížeč, URL portálu).")

    # Podmínka 2: Je v něm report pro každý padající test
    failing_tests = get_failing_tests_from_junit(project_root)

    # Extrakce karet vad z HTML
    # Karty jsou v <div class="defect-card ... id="BUG-XX">...</div>
    card_pattern = r'(<div[^>]*class="[^"]*defect-card[^"]*"[^>]*id="([^"]+)"[^>]*>.*?</div>\s*</div>)'
    cards = re.findall(r'<div[^>]*class="[^"]*defect-card[^"]*".*?(?=<div[^>]*class="[^"]*defect-card|\Z)', html_content, re.DOTALL)

    if failing_tests:
        for ft in failing_tests:
            # Hledáme, zda je test zastoupen v některé kartě
            test_repr = ft["clean_name"]
            found_card = False
            for card in cards:
                if test_repr in card or ft["name"] in card:
                    found_card = True
                    break
            if not found_card:
                issues.append(f"Pro padající test '{ft['name']}' chybí report v HTML přehledu.")

    # Podmínka 3: Každý report má všechna povinná pole
    if cards:
        for idx, card in enumerate(cards, 1):
            id_match = re.search(r'id=["\'](BUG-\d+)["\']', card)
            card_id = id_match.group(1) if id_match else f"Vada #{idx}"

            test_name_match = re.search(r'<strong>(.*?)</strong>', card)
            test_name = test_name_match.group(1) if test_name_match else "Neznámý test"

            missing_fields = validate_defect_card(card, project_root, html_dir)
            if missing_fields:
                issues.append(f"Karta '{card_id}' ({test_name}) nemá splněna povinná pole: {', '.join(missing_fields)}.")
    else:
        # Pokud nejsou žádné karty vad, zkontrolujeme, zda report explicitně deklaruje úspěch
        is_success = "Všechny automatizované testy proběhly bez chyb" in html_content or "success-banner" in html_content
        if not is_success and failing_tests:
            issues.append("V HTML přehledu chybí karty identifikovaných vad.")

    is_valid = len(issues) == 0
    return is_valid, issues


def main():
    # 1. Čtení stdin s JSON kontextem Antigravity (bezpečně s timeoutem)
    hook_input = read_stdin_with_timeout(timeout_sec=0.5)

    # Určení kořene projektu
    project_root = find_project_root(hook_input)

    # Vyhodnocení Definice hotovo
    is_valid, issues = verify_definition_of_done(project_root)

    if is_valid:
        # Všechny požadavky jsou 100% splněny -> povolíme ukončení agenta
        response = {
            "decision": "allow"
        }
        sys.stderr.write("✅ Definice hotovo (Stop Hook): HTML přehled je platný, všechny padající testy mají report se všemi povinnými poli.\n")
    else:
        # Podmínky nejsou splněny -> nepustíme agenta skončit a předáme důvod
        reasons_text = "\n".join([f"  • {issue}" for issue in issues])
        response = {
            "decision": "continue",
            "reason": (
                "⚠️ STOP HOOK: Definice hotovo není splněna! "
                "Agent nesmí skončit, dokud nebudou splněny všechny následující požadavky:\n"
                f"{reasons_text}\n\n"
                "Opravte chyby, spusťte generování reportu 'python .agents/skills/bug-report/scripts/generate_bug_report.py' "
                "a zajistěte, aby každý padající test měl kompletní report s kroky k reprodukci, očekávaným i skutečným výsledkem, "
                "prostředím a odkazem na existující důkaz (screenshot nebo trace)."
            )
        }
        sys.stderr.write(f"❌ Stop Hook odmítl ukončení:\n{response['reason']}\n")

    # Výstup na stdout
    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
