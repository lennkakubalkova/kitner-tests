#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_bug_report_dod.py
------------------------
Stop hook pro Antigravity Agent (podle kapitoly 5):
1. ZASAHUJE POUZE TEHDY, KDYŽ BĚŽEL SKILL bug-report:
   - Pokud uživatel ani agent v tomto turnu/úloze nepracoval se skillem bug-report
     (ani nespustil testy pro hlášení chyb), hook okamžitě povolí ukončení {"decision": "allow"}.
2. KONTROLUJE DETAILNÍ OBSAH REPORTU, NE JEN EXISTENCI SOUBORU:
   - Existence a validita HTML struktury docs/bug_report.html.
   - Aktuálnost reportu (nesmí být zastaralý vůči poslednímu běhu testů).
   - Kompletní pokrytí všech padajících testů z posledního testovacího běhu (JUnit XML).
   - Kontrola všech povinných polí v každém záznamu vady (kroky k reprodukci, očekávaný výsledek,
     skutečný výsledek, prostředí, fyzická existence a neprázdnost screenshotu / trace souboru).

Používá výhradně standardní knihovnu Pythonu.
"""

import os
import sys
import re
import json
import time
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
    ws_paths = hook_input.get("workspacePaths", [])
    if ws_paths and os.path.exists(ws_paths[0]):
        return os.path.abspath(ws_paths[0])

    cwd = hook_input.get("cwd")
    if cwd and os.path.exists(cwd):
        return os.path.abspath(cwd)

    curr = os.path.abspath(os.getcwd())
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, "pytest.ini")) or os.path.exists(os.path.join(curr, ".git")):
            return curr
        curr = os.path.dirname(curr)

    return os.path.abspath(os.getcwd())


def is_skill_active_in_session(hook_input: dict, project_root: str) -> bool:
    """
    KAPITOLA 5: Hook má zasahovat JEN TEHDY, když běžel tenhle skill!
    Zjišťuje, zda v aktuální konverzaci či v posledním turnu byl aktivován skill bug-report.
    """
    # 1. Kontrola posledního uživatelského vstupu
    last_user_input = hook_input.get("lastUserInput", "").lower()
    bug_report_keywords = [
        "bug-report", "bug_report", "reportovat chyb", "reportování chyb", "hlášení chyb",
        "přehled chyb", "vytvořte report", "vytvořit report", "defect report", "stop hook",
        "kapitola 5", "definici hotovo vynuťte", "ověřte hook", "padající test"
    ]
    if any(kw in last_user_input for kw in bug_report_keywords):
        return True

    # 2. Kontrola transcriptu konverzace (posledních kroků agenta)
    transcript_path = hook_input.get("transcriptPath")
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as tf:
                lines = tf.readlines()[-60:]
                tail = "".join(lines).lower()
                if "bug-report" in tail or "generate_bug_report" in tail or "verify_bug_report_dod" in tail:
                    return True
        except Exception:
            pass

    # 3. Kontrola markeru posledního běhu skriptu (.last_run)
    marker_file = os.path.join(project_root, ".agents", "skills", "bug-report", ".last_run")
    if os.path.exists(marker_file):
        try:
            mtime = os.path.getmtime(marker_file)
            # Pokud skript běžel v posledních 30 minutách
            if (time.time() - mtime) < 1800:
                return True
        except Exception:
            pass

    return False


def get_failing_tests_from_junit(project_root: str) -> tuple[list[dict], float | None]:
    """Získá seznam padajících testů z posledního JUnit XML reportu a jeho timestamp."""
    junit_candidates = [
        os.path.join(project_root, "reports", "junit_temp_report.xml"),
        os.path.join(project_root, "reports", "junit_report.xml"),
    ]

    for jpath in junit_candidates:
        if os.path.exists(jpath):
            try:
                mtime = os.path.getmtime(jpath)
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
                return failing, mtime
            except Exception:
                pass

    return [], None


def validate_defect_card_content(card_html: str, html_dir: str) -> list[str]:
    """
    KAPITOLA 5: Kontrola OBSAHU každé karty vady v reportu (nejen prázdné tagy):
    - Kroky k reprodukci: musí obsahovat alespoň jeden neprázdný krok s reálným textem
    - Očekávaný výsledek: smysluplný neprázdný popis očekávání
    - Skutečný výsledek: smysluplný popis zjištěného stavu / chyby
    - Prostředí: prostředí musí být uvedeno
    - Odkaz na důkaz: musí existovat odkaz na screenshot / trace a soubor musí fyzicky existovat na disku s velikostí > 0 B
    """
    missing = []

    # 1. Kroky k reprodukci (repro-steps)
    has_valid_steps = False
    repro_match = re.search(r'<ol[^>]*class="[^"]*repro-steps[^"]*"[^>]*>(.*?)</ol>', card_html, re.DOTALL)
    if repro_match:
        li_items = re.findall(r'<li[^>]*>(.*?)</li>', repro_match.group(1), re.DOTALL)
        # Ověření, že kroky obsahují skutečný obsah (> 5 znaků)
        valid_items = [re.sub(r'<[^>]+>', '', li).strip() for li in li_items if len(re.sub(r'<[^>]+>', '', li).strip()) > 5]
        if len(valid_items) >= 1:
            has_valid_steps = True

    if not has_valid_steps:
        missing.append("Kroky k reprodukci (chybí smysluplné číslované kroky v <ol class='repro-steps'>)")

    # 2. Očekávaný výsledek (expected result)
    has_valid_expected = False
    exp_match = re.search(r'class="[^"]*expected-box[^"]*"[^>]*>.*?<p[^>]*>(.*?)</p>', card_html, re.DOTALL)
    if exp_match:
        exp_text = re.sub(r'<[^>]+>', '', exp_match.group(1)).strip()
        if len(exp_text) > 8:
            has_valid_expected = True

    if not has_valid_expected:
        missing.append("Očekávaný výsledek (chybí nebo je prázdný v <div class='expected-box'>)")

    # 3. Skutečný výsledek (actual result)
    has_valid_actual = False
    act_match = re.search(r'class="[^"]*actual-box[^"]*"[^>]*>.*?<p[^>]*>(.*?)</p>', card_html, re.DOTALL)
    if act_match:
        act_text = re.sub(r'<[^>]+>', '', act_match.group(1)).strip()
        if len(act_text) > 8:
            has_valid_actual = True

    if not has_valid_actual:
        missing.append("Skutečný výsledek (chybí nebo je prázdný v <div class='actual-box'>)")

    # 4. Odkaz na důkaz a fyzická kontrola existence souboru na disku
    has_valid_evidence = False
    evidence_desc = []

    # Screenshot kontrola
    scr_matches = re.findall(r'<a\s+[^>]*href=["\']([^"\']+\.png)["\']', card_html, re.IGNORECASE)
    for scr in scr_matches:
        abs_scr = os.path.normpath(os.path.join(html_dir, scr)) if not os.path.isabs(scr) else scr
        if os.path.exists(abs_scr) and os.path.getsize(abs_scr) > 100:
            has_valid_evidence = True
            evidence_desc.append(f"Screenshot ({os.path.basename(abs_scr)})")

    # Trace kontrola
    trc_matches = re.findall(r'<a\s+[^>]*href=["\']([^"\']+\.zip)["\']', card_html, re.IGNORECASE)
    for trc in trc_matches:
        abs_trc = os.path.normpath(os.path.join(html_dir, trc)) if not os.path.isabs(trc) else trc
        if os.path.exists(abs_trc) and os.path.getsize(abs_trc) > 100:
            has_valid_evidence = True
            evidence_desc.append(f"Trace ({os.path.basename(abs_trc)})")

    if not has_valid_evidence:
        missing.append("Odkaz na platný existující důkaz (screenshot .png nebo trace .zip soubor větší než 100 B)")

    return missing


def verify_definition_of_done(project_root: str) -> tuple[bool, list[str]]:
    """
    Detailní kontrola obsahu a pravidel Definice hotovo:
    1. Existuje HTML přehled.
    2. HTML má platnou a neporušenou strukturu včetně hlavičky s prostředím.
    3. Je v něm report pro každý padající test z testovacího běhu.
    4. Každý report má všechna povinná pole s reálným obsahem.
    """
    issues = []

    html_path = os.path.join(project_root, "docs", "bug_report.html")
    html_dir = os.path.dirname(html_path)

    # 1. Existence HTML souboru
    if not os.path.exists(html_path):
        issues.append(f"HTML přehled chyb neexistuje: '{os.path.relpath(html_path, project_root)}'.")
        return False, issues

    try:
        html_mtime = os.path.getmtime(html_path)
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        issues.append(f"Nelze přečíst HTML soubor '{html_path}': {e}")
        return False, issues

    # 2. Kontrola integrity HTML obsahu (ne jen pouhá existence souboru)
    if len(html_content.strip()) < 300:
        issues.append(f"Soubor '{html_path}' je příliš krátký nebo neúplný (délka {len(html_content.strip())} znaků).")
        return False, issues

    if "<!DOCTYPE html>" not in html_content or "</html>" not in html_content:
        issues.append("Soubor 'docs/bug_report.html' není platný HTML5 dokument.")

    if 'class="kpi-grid"' not in html_content:
        issues.append("V HTML přehledu chybí souhrnné metriky (kpi-grid).")

    # 3. Kontrola specifikace testovacího prostředí
    has_env = "env-tag" in html_content and ("Prostředí:" in html_content or "http" in html_content)
    if not has_env:
        issues.append("V HTML přehledu chybí specifikace testovacího prostředí (URL, OS, prohlížeč).")

    # 4. Kontrola padajících testů vůči obsahu reportu
    failing_tests, junit_mtime = get_failing_tests_from_junit(project_root)

    # Kontrola aktuálnosti: pokud JUnit běžel podstatně později než HTML report
    if junit_mtime and (junit_mtime - html_mtime) > 10.0:
        issues.append("HTML report je zastaralý – byl vygenerován dříve než poslední testovací běh. Spusťte generování znovu.")

    # Extrakce karet vad
    cards = re.findall(r'<div[^>]*class="[^"]*defect-card[^"]*".*?(?=<div[^>]*class="[^"]*defect-card|\Z)', html_content, re.DOTALL)

    if failing_tests:
        for ft in failing_tests:
            # Kontrola, zda je pro padající test obsažena karta vady
            test_found = False
            for card in cards:
                if ft["clean_name"] in card or ft["name"] in card:
                    test_found = True
                    break
            if not test_found:
                issues.append(f"Pro padající test '{ft['name']}' chybí karta vady v HTML přehledu.")

    # 5. Kontrola obsahu každého reportu (povinná pole)
    if cards:
        for idx, card in enumerate(cards, 1):
            id_match = re.search(r'id=["\'](BUG-\d+)["\']', card)
            card_id = id_match.group(1) if id_match else f"BUG-{idx:02d}"

            test_name_match = re.search(r'<strong>(.*?)</strong>', card)
            test_name = test_name_match.group(1) if test_name_match else "Neznámý test"

            missing = validate_defect_card_content(card, html_dir)
            if missing:
                issues.append(f"Vada '{card_id}' ({test_name}) nemá řádně vyplněna pole: {'; '.join(missing)}.")
    else:
        # Žádné karty vad: zkontrolujeme, zda report legitimně deklaruje úspěch (0 vad)
        is_success = "success-banner" in html_content or "Všechny automatizované testy proběhly bez chyb" in html_content
        if not is_success and failing_tests:
            issues.append("V HTML přehledu chybí záznamy zjištěných vad pro padající testy.")

    is_valid = len(issues) == 0
    return is_valid, issues


def main():
    # 1. Načtení kontextu hooku
    hook_input = read_stdin_with_timeout(timeout_sec=0.5)

    # 2. Určení kořene projektu
    project_root = find_project_root(hook_input)

    # 3. KAPITOLA 5: Kontrola, zda v tomto běhu běžel skill bug-report
    if not is_skill_active_in_session(hook_input, project_root):
        # Skill nebyl v tomto běhu aktivován -> hook nekontroluje a povolí ukončení
        sys.stderr.write("ℹ️ Stop Hook: Skill bug-report nebyl v tomto turnu aktivován. Kontrola přeskočena (allow).\n")
        print(json.dumps({"decision": "allow"}, ensure_ascii=False))
        return

    # 4. Pokud skill běžel, provede se striktní kontrola obsahu reportu
    is_valid, issues = verify_definition_of_done(project_root)

    if is_valid:
        response = {
            "decision": "allow"
        }
        sys.stderr.write("✅ Definice hotovo (Stop Hook): HTML přehled i jeho obsah jsou 100% v pořádku.\n")
    else:
        reasons_text = "\n".join([f"  • {issue}" for issue in issues])
        response = {
            "decision": "continue",
            "reason": (
                "⚠️ STOP HOOK (Definice hotovo pro bug-report): Agent nesmí skončit, dokud nejsou splněny podmínky:\n"
                f"{reasons_text}\n\n"
                "Zajistěte, aby existoval HTML přehled 'docs/bug_report.html' a obsahoval kompletní záznam "
                "pro každý padající test se všemi povinnými poli (kroky k reprodukci, očekávaný výsledek, "
                "skutečný výsledek, prostředí a odkaz na platný důkaz)."
            )
        }
        sys.stderr.write(f"❌ Stop Hook odmítl ukončení:\n{response['reason']}\n")

    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
