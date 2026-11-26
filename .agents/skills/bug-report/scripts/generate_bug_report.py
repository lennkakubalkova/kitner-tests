#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_bug_report.py
----------------------
Spustí automatizované testy (Playwright + pytest), zachytí veškeré selhání (včetně screenshotů
a Playwright trace důkazů), identifikuje chyby, analyzuje kroky k reprodukci, očekávané a skutečné
výsledky a vygeneruje interaktivní HTML Defect Report.

Použití:
    python generate_bug_report.py
    python generate_bug_report.py --test-path tests/test_courses.py
    python generate_bug_report.py -k "create_course"
    python generate_bug_report.py --output docs/bug_report.html --evidence-dir docs/evidence
"""

import os
import sys
import re
import json
import time
import shutil
import platform
import argparse
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime


def get_project_root() -> str:
    """Vrátí absolutní cestu ke kořeni projektu."""
    current = os.path.abspath(os.getcwd())
    # Pokud běžíme ze složky scripts, posuneme se výš
    if os.path.basename(current) in ("scripts", "bug-report", ".agents"):
        while not os.path.exists(os.path.join(current, "pytest.ini")) and os.path.dirname(current) != current:
            current = os.path.dirname(current)
    return current


def get_python_executable(project_root: str) -> str:
    """Najde správný Python s nainstalovaným pytest a playwright (preferuje .venv)."""
    venv_python = os.path.join(project_root, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    venv_python_unix = os.path.join(project_root, ".venv", "bin", "python")
    if os.path.exists(venv_python_unix):
        return venv_python_unix
    return sys.executable


def get_environment_info(project_root: str) -> dict:
    """Získá podrobné informace o testovacím prostředí."""
    config_file = os.path.join(project_root, "config", "config.py")
    base_url = "http://testovani.kitner.cz"
    browser = "Chromium (Headless)"

    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                content = f.read()
                url_match = re.search(r'BASE_URL\s*=\s*["\']([^"\']+)["\']', content)
                if url_match:
                    base_url = url_match.group(1)
                headless_match = re.search(r'HEADLESS\s*=\s*(True|False)', content)
                if headless_match and headless_match.group(1) == "False":
                    browser = "Chromium (Headed)"
        except Exception:
            pass

    return {
        "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "python_version": platform.python_version(),
        "browser": browser,
        "base_url": base_url,
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "hostname": platform.node()
    }


def parse_docstring_info(test_file_path: str, test_name: str) -> dict:
    """
    Parsuje docstring a kód testovací funkce:
    - Kroky k reprodukci
    - Očekávaný výsledek
    - Mapování na User Story / Test Case
    """
    clean_test_name = test_name.split("[")[0]
    result = {
        "steps": [],
        "expected": "Operace proběhne úspěšně a uživatelské rozhraní odpovídá specifikaci.",
        "user_story": "Neznámá US",
        "tc_id": "",
        "raw_docstring": ""
    }

    if not os.path.exists(test_file_path):
        return result

    try:
        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Vyhledání testovací metody
        pattern = rf"def\s+{clean_test_name}\s*\([^)]*\):\s*(?:\"\"\"(.*?)\"\"\"|'''(.*?)''')"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            doc = (match.group(1) or match.group(2) or "").strip()
            result["raw_docstring"] = doc

            # User Story a TC detekce
            tc_match = re.search(r"\b(TC[-_]?\d+)\b", doc)
            if tc_match:
                result["tc_id"] = tc_match.group(1).upper().replace("_", "-")

            us_match = re.search(r"\bUS[-_]?(\d+)\b", doc)
            if us_match:
                result["user_story"] = f"US-{int(us_match.group(1)):02d}"
            else:
                # Zkusíme najít v hlavičce souboru
                header_us = re.search(r"\bUS[-_]?(\d+)\b", content[:1000])
                if header_us:
                    result["user_story"] = f"US-{int(header_us.group(1)):02d}"

            # Extrakce kroků z docstringu (Kontroly / Kroky)
            steps_match = re.search(r"(?:Kontroly|Kroky|Steps):\s*\n((?:\s*\d+\..*?\n)+)", doc, re.IGNORECASE)
            if steps_match:
                lines = steps_match.group(1).strip().splitlines()
                for line in lines:
                    line_clean = re.sub(r"^\s*\d+\.\s*", "", line).strip()
                    if line_clean:
                        result["steps"].append(line_clean)

            # Extrakce očekávaného výsledku
            exp_match = re.search(r"(?:Očekávaný výsledek|Expected result|Výsledek):\s*(.*?)(?:\n\s*\n|\Z)", doc, re.IGNORECASE | re.DOTALL)
            if exp_match:
                result["expected"] = exp_match.group(1).strip()
            elif result["steps"]:
                # Poslední kontrolní krok bývá očekávaným výsledkem
                result["expected"] = f"Úspěšné ověření: {result['steps'][-1]}"

    except Exception:
        pass

    # Heuristické mapování na User Story, pokud není explicitně v docstringu
    if result["user_story"] == "Neznámá US":
        t_low = clean_test_name.lower()
        f_low = os.path.basename(test_file_path).lower()
        if "create_course" in t_low or "add_course" in t_low or ("modal" in t_low and "course" in t_low):
            result["user_story"] = "US-14: Vytvoření nového kurzu lektorem"
        elif "iteration" in t_low or "termin" in t_low:
            result["user_story"] = "US-15: Vypsání termínu kurzu lektorem"
        elif "participants" in t_low or "ucastnici" in t_low:
            result["user_story"] = "US-16: Zobrazení přihlášených účastníků pro lektora"
        elif "filter" in t_low or "search" in t_low or "filtrovani" in t_low:
            result["user_story"] = "US-11: Vyhledávání a filtrování kurzů dle kapacity"
        elif "enroll" in t_low or "zapis" in t_low:
            result["user_story"] = "US-12: Zápis studenta na vypsaný termín kurzu"
        elif "my_courses" in t_low or "moje_kurzy" in t_low:
            result["user_story"] = "US-13: Přehled zapsaných kurzů (Moje kurzy)"
        elif "login" in t_low or "prihlaseni" in t_low:
            result["user_story"] = "US-03: Přihlašování uživatelů a autorizace rolí"
        elif "logout" in t_low or "odhlaseni" in t_low:
            result["user_story"] = "US-04: Odhlášení ze systému a ukončení sezení"
        elif "forgot_password" in t_low or "zapomenute_heslo" in t_low:
            result["user_story"] = "US-05: Obnova zapomenutého hesla"
        elif "register" in t_low or "registration" in t_low or "registrace" in t_low:
            result["user_story"] = "US-02: Registrace zákaznického účtu a validace"
        elif "portal" in t_low:
            result["user_story"] = "US-01: Úvodní navigační rozcestník portálu"
        elif "profile" in t_low:
            result["user_story"] = "US-18: Uživatelský profil a správa údajů"
        elif "navigation" in t_low:
            result["user_story"] = "US-19: Globální navigace a autorizační hranice"
        elif "detail" in t_low:
            result["user_story"] = "US-10: Zobrazení detailu kurzu a termínů"
        elif "courses" in f_low:
            result["user_story"] = "US-09: Veřejný přehled a katalog kurzů"

    # Pokud se nepodařilo vyčíst kroky z docstringu, sestavíme generické kroky
    if not result["steps"]:
        result["steps"] = [
            f"Otevři testovací prostředí portálu na definované URL.",
            f"Proveď akce definované v testu '{clean_test_name}'.",
            f"Zkontroluj odezvu aplikace a aserce prvku na stránce."
        ]

    return result


def determine_severity(error_text: str, test_name: str) -> str:
    """Určí závažnost vady (Severity) podle typu chyby a kontextu."""
    err_lower = error_text.lower()

    if "500 internal server error" in err_lower or "server error" in err_lower or "fatal error" in err_lower:
        return "Blocker"
    elif "timeout" in err_lower and ("waiting for event" in err_lower or "wait_for_url" in err_lower):
        return "Critical"
    elif "assertionerror" in err_lower and ("login" in test_name or "register" in test_name or "enroll" in test_name):
        return "Critical"
    elif "assertionerror" in err_lower:
        return "Major"
    elif "timeout" in err_lower:
        return "Major"
    else:
        return "Minor"


def run_tests_and_collect_failures(
    project_root: str,
    python_bin: str,
    test_path: str,
    k_filter: str | None,
    evidence_dir: str,
    from_junit: str | None = None
) -> tuple[int, list[dict], float]:
    """
    Spustí pytest s generováním JUnit XML a aktivním zachycováním screenshotů/trace při chybě,
    nebo zpracuje existující JUnit XML report.
    """
    junit_file = from_junit if from_junit else os.path.join(project_root, "reports", "junit_temp_report.xml")
    os.makedirs(os.path.dirname(junit_file), exist_ok=True)
    os.makedirs(evidence_dir, exist_ok=True)

    duration = 0.0
    if not from_junit:
        cmd = [
            python_bin,
            "-m", "pytest",
            test_path,
            f"--junitxml={junit_file}",
            "-v",
            "--tb=short"
        ]
        if k_filter:
            cmd.extend(["-k", k_filter])

        env = os.environ.copy()
        env["EVIDENCE_DIR"] = os.path.abspath(evidence_dir)
        env["PLAYWRIGHT_TRACING"] = "1"

        print(f"🚀 Spouštím testy: {' '.join(cmd)}")
        start_time = time.time()
        proc = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
        duration = time.time() - start_time

        print(f"⏱️ Běh testů dokončen za {duration:.2f} s (Exit kód: {proc.returncode})")
    else:
        print(f"📂 Načítám data z existujícího JUnit XML reportu: {from_junit}")

    total_tests = 0
    failures = []

    if os.path.exists(junit_file):
        try:
            tree = ET.parse(junit_file)
            root = tree.getroot()

            # Zpracování testsuite / testsuites
            suites = root.findall(".//testsuite") if root.tag != "testsuite" else [root]

            for suite in suites:
                total_tests += int(suite.attrib.get("tests", 0))

                for tc in suite.findall("testcase"):
                    classname = tc.attrib.get("classname", "")
                    test_func_name = tc.attrib.get("name", "")
                    tc_file = tc.attrib.get("file", "")

                    failure = tc.find("failure")
                    error = tc.find("error")
                    problem = failure if failure is not None else error

                    if problem is not None:
                        err_msg = problem.attrib.get("message", "Test selhal")
                        stacktrace = problem.text or ""

                        # Hledáme odpovídající soubor testu
                        if not tc_file:
                            # Odvodit z classname (např. tests.test_courses.TestCourses)
                            parts = classname.split(".")
                            if len(parts) >= 2:
                                tc_file = os.path.join(project_root, parts[0], parts[1] + ".py")
                        else:
                            tc_file = os.path.join(project_root, tc_file)

                        # Parsování docstringu a detailů
                        doc_info = parse_docstring_info(tc_file, test_func_name)

                        # Hledání screenshotu a trace
                        safe_name = re.sub(r"[^\w\-.]", "_", test_func_name)
                        screenshot_file = os.path.join(evidence_dir, "screenshots", f"{safe_name}.png")
                        trace_file = os.path.join(evidence_dir, "traces", f"{safe_name}.zip")

                        has_screenshot = os.path.exists(screenshot_file)
                        has_trace = os.path.exists(trace_file)

                        # Pokud přímý screenshot chybí, ale trace byl zaznamenán, získáme screenshot z trace zipu
                        if not has_screenshot and has_trace:
                            try:
                                import zipfile
                                with zipfile.ZipFile(trace_file, 'r') as zf:
                                    pngs = [n for n in zf.namelist() if n.endswith('.png')]
                                    if pngs:
                                        last_png = pngs[-1]
                                        os.makedirs(os.path.dirname(screenshot_file), exist_ok=True)
                                        with zf.open(last_png) as src, open(screenshot_file, "wb") as dst:
                                            dst.write(src.read())
                                        has_screenshot = True
                            except Exception:
                                pass

                        # Skutečný výsledek a titulek vady (čistý první řádek chyby)
                        err_first_line = err_msg.splitlines()[0] if err_msg else "Test selhal"
                        actual_result = err_first_line
                        defect_title = err_first_line

                        failures.append({
                            "id": f"BUG-{len(failures) + 1:02d}",
                            "test_name": test_func_name,
                            "classname": classname,
                            "file": os.path.relpath(tc_file, project_root) if os.path.exists(tc_file) else tc_file,
                            "user_story": doc_info["user_story"],
                            "tc_id": doc_info["tc_id"],
                            "severity": determine_severity(err_msg + " " + stacktrace, test_func_name),
                            "error_message": defect_title,
                            "actual_result": actual_result,
                            "expected_result": doc_info["expected"],
                            "steps_to_reproduce": doc_info["steps"],
                            "stacktrace": stacktrace,
                            "screenshot_path": os.path.relpath(screenshot_file, os.path.dirname(os.path.abspath(evidence_dir))) if has_screenshot else None,
                            "trace_path": os.path.relpath(trace_file, os.path.dirname(os.path.abspath(evidence_dir))) if has_trace else None,
                            "has_screenshot": has_screenshot,
                            "has_trace": has_trace
                        })

        except Exception as e:
            print(f"⚠️ Chyba při parsování JUnit reportu: {e}")

    return total_tests, failures, duration


def generate_html_bug_report(
    output_html_path: str,
    total_tests: int,
    failures: list[dict],
    duration: float,
    env_info: dict,
    evidence_dir: str
):
    """Vygeneruje moderní, plně responzivní HTML report všech zjištěných chyb."""
    passed_tests = max(0, total_tests - len(failures))
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0

    # Počty dle závažnosti
    severity_counts = {
        "Blocker": len([f for f in failures if f["severity"] == "Blocker"]),
        "Critical": len([f for f in failures if f["severity"] == "Critical"]),
        "Major": len([f for f in failures if f["severity"] == "Major"]),
        "Minor": len([f for f in failures if f["severity"] == "Minor"]),
    }

    # Relativní cesta ze složky HTML do evidence
    html_dir = os.path.dirname(os.path.abspath(output_html_path))

    cards_html = []
    for defect in failures:
        # Přepočet relativních cest k důkazům vzhledem k HTML souboru
        screenshot_rel = None
        trace_rel = None

        if defect["has_screenshot"]:
            safe_name = re.sub(r"[^\w\-.]", "_", defect["test_name"])
            abs_scr = os.path.join(evidence_dir, "screenshots", f"{safe_name}.png")
            if os.path.exists(abs_scr):
                screenshot_rel = os.path.relpath(abs_scr, html_dir).replace("\\", "/")

        if defect["has_trace"]:
            safe_name = re.sub(r"[^\w\-.]", "_", defect["test_name"])
            abs_trc = os.path.join(evidence_dir, "traces", f"{safe_name}.zip")
            if os.path.exists(abs_trc):
                trace_rel = os.path.relpath(abs_trc, html_dir).replace("\\", "/")

        severity_class = f"badge-{defect['severity'].lower()}"

        steps_li = "".join([f"<li>{s}</li>" for s in defect["steps_to_reproduce"]])

        screenshot_markup = ""
        if screenshot_rel:
            screenshot_markup = f"""
            <div class="evidence-box">
                <div class="evidence-title">📸 Snímek obrazovky při selhání (Screenshot):</div>
                <a href="{screenshot_rel}" target="_blank" title="Klikněte pro zobrazení v plném rozlišení">
                    <img src="{screenshot_rel}" alt="Důkaz chyby {defect['id']}" class="evidence-thumb" />
                </a>
                <div class="evidence-hint">Kliknutím na náhled otevřete snímek v plném rozlišení.</div>
            </div>
            """
        else:
            screenshot_markup = """
            <div class="evidence-box evidence-missing">
                <span class="text-muted">Snímek obrazovky není k dispozici (test selhal před inicializací stránky nebo v setupu).</span>
            </div>
            """

        trace_markup = ""
        if trace_rel:
            trace_markup = f"""
            <div class="trace-box">
                <div class="evidence-title">🔍 Playwright Trace (Kompletní záznam průběhu):</div>
                <a href="{trace_rel}" download class="btn-trace">
                    📥 Stáhnout záznam Trace ({os.path.basename(trace_rel)})
                </a>
                <span class="trace-tip">Záznam otevřete příkazem: <code>playwright show-trace {os.path.basename(trace_rel)}</code></span>
            </div>
            """

        clean_stack = defect["stacktrace"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        cards_html.append(f"""
        <div class="defect-card severity-{defect['severity'].lower()}" id="{defect['id']}">
            <div class="defect-header">
                <div class="defect-header-left">
                    <span class="defect-id">{defect['id']}</span>
                    <span class="badge {severity_class}">{defect['severity']}</span>
                    <span class="badge badge-us">{defect['user_story']}</span>
                    {f'<span class="badge badge-tc">{defect["tc_id"]}</span>' if defect["tc_id"] else ''}
                </div>
                <div class="defect-header-right">
                    <span class="defect-file"><code>{defect['file']}</code> :: <strong>{defect['test_name']}</strong></span>
                </div>
            </div>

            <div class="defect-body">
                <h3 class="defect-title">{defect['error_message']}</h3>

                <div class="defect-grid">
                    <div class="defect-col">
                        <h4>📋 Kroky k reprodukci:</h4>
                        <ol class="repro-steps">
                            {steps_li}
                        </ol>
                    </div>

                    <div class="defect-col">
                        <div class="result-box expected-box">
                            <span class="result-label">✅ Očekávaný výsledek:</span>
                            <p>{defect['expected_result']}</p>
                        </div>
                        <div class="result-box actual-box">
                            <span class="result-label">❌ Skutečný výsledek:</span>
                            <p>{defect['actual_result']}</p>
                        </div>
                    </div>
                </div>

                <div class="defect-evidence-section">
                    <h4>🖼️ Důkazy o selhání (Evidence):</h4>
                    <div class="evidence-container">
                        {screenshot_markup}
                        {trace_markup}
                    </div>
                </div>

                <details class="stacktrace-details">
                    <summary>🛠️ Technický stacktrace a detaily selhání</summary>
                    <pre class="stacktrace-code"><code>{clean_stack}</code></pre>
                </details>
            </div>
        </div>
        """)

    all_cards_str = "\n".join(cards_html) if cards_html else """
    <div class="success-banner">
        <h2>🎉 Všechny automatizované testy proběhly bez chyb!</h2>
        <p>V testované verzi nebyly identifikovány žádné vady ani regresní selhání.</p>
    </div>
    """

    html_content = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Defect Report - Přehled nalezených chyb v automatizovaných testech</title>
    <style>
        :root {{
            --bg-body: #0f172a;
            --bg-card: #1e293b;
            --bg-card-alt: #334155;
            --border-color: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-blue: #38bdf8;
            --color-blocker: #dc2626;
            --color-critical: #ea580c;
            --color-major: #f59e0b;
            --color-minor: #3b82f6;
            --color-success: #10b981;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-main);
            font-family: var(--font-family);
            line-height: 1.5;
            padding: 24px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header */
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .title-group h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .title-group p {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 4px;
        }}

        .env-badge-group {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .env-tag {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .env-tag strong {{
            color: var(--text-main);
        }}

        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent-blue);
        }}

        .kpi-value {{
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 4px;
        }}

        .kpi-label {{
            color: var(--text-muted);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .kpi-total .kpi-value {{ color: var(--accent-blue); }}
        .kpi-passed .kpi-value {{ color: var(--color-success); }}
        .kpi-failed .kpi-value {{ color: #ef4444; }}
        .kpi-rate .kpi-value {{ color: #a855f7; }}

        /* Filter bar */
        .filter-bar {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 14px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .filter-buttons {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .btn-filter {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}

        .btn-filter:hover, .btn-filter.active {{
            background: var(--accent-blue);
            color: #0f172a;
            border-color: var(--accent-blue);
        }}

        /* Defect Cards */
        .defects-list {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .defect-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 6px solid #ef4444;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}

        .defect-card.severity-blocker {{ border-left-color: var(--color-blocker); }}
        .defect-card.severity-critical {{ border-left-color: var(--color-critical); }}
        .defect-card.severity-major {{ border-left-color: var(--color-major); }}
        .defect-card.severity-minor {{ border-left-color: var(--color-minor); }}

        .defect-header {{
            background: rgba(15, 23, 42, 0.6);
            border-bottom: 1px solid var(--border-color);
            padding: 14px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .defect-header-left {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .defect-id {{
            font-weight: 800;
            font-size: 1.1rem;
            color: #ffffff;
            background: #0f172a;
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}

        .badge {{
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .badge-blocker {{ background: rgba(220, 38, 38, 0.2); color: #fca5a5; border: 1px solid var(--color-blocker); }}
        .badge-critical {{ background: rgba(234, 88, 12, 0.2); color: #fdba74; border: 1px solid var(--color-critical); }}
        .badge-major {{ background: rgba(245, 158, 11, 0.2); color: #fde047; border: 1px solid var(--color-major); }}
        .badge-minor {{ background: rgba(59, 130, 246, 0.2); color: #93c5fd; border: 1px solid var(--color-minor); }}
        .badge-us {{ background: rgba(168, 85, 247, 0.2); color: #d8b4fe; border: 1px solid #a855f7; }}
        .badge-tc {{ background: rgba(20, 184, 166, 0.2); color: #5eead4; border: 1px solid #14b8a6; }}

        .defect-file {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .defect-file code {{
            background: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
            color: var(--accent-blue);
        }}

        .defect-body {{
            padding: 20px;
        }}

        .defect-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #f87171;
            margin-bottom: 18px;
            line-height: 1.4;
        }}

        .defect-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .defect-col h4 {{
            font-size: 0.95rem;
            color: var(--text-muted);
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .repro-steps {{
            background: #0f172a;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px 20px 16px 36px;
            color: #e2e8f0;
            font-size: 0.9rem;
        }}

        .repro-steps li {{
            margin-bottom: 8px;
        }}

        .repro-steps li:last-child {{
            margin-bottom: 0;
        }}

        .result-box {{
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 12px;
            font-size: 0.9rem;
        }}

        .result-label {{
            display: block;
            font-weight: 700;
            margin-bottom: 4px;
            font-size: 0.85rem;
            text-transform: uppercase;
        }}

        .expected-box {{
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #a7f3d0;
        }}

        .actual-box {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
        }}

        /* Evidence */
        .defect-evidence-section {{
            margin-top: 20px;
            border-top: 1px solid var(--border-color);
            padding-top: 18px;
        }}

        .defect-evidence-section h4 {{
            font-size: 0.95rem;
            color: var(--text-muted);
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .evidence-container {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .evidence-box {{
            flex: 1;
            min-width: 320px;
            background: #0f172a;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px;
        }}

        .evidence-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 10px;
        }}

        .evidence-thumb {{
            width: 100%;
            max-height: 280px;
            object-fit: contain;
            background: #000;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            cursor: pointer;
            transition: opacity 0.2s;
        }}

        .evidence-thumb:hover {{
            opacity: 0.9;
        }}

        .evidence-hint {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 6px;
            text-align: center;
        }}

        .trace-box {{
            flex: 1;
            min-width: 320px;
            background: #0f172a;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .btn-trace {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-card-alt);
            color: var(--text-main);
            padding: 10px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            border: 1px solid var(--border-color);
            margin-bottom: 10px;
            transition: all 0.2s ease;
        }}

        .btn-trace:hover {{
            background: var(--accent-blue);
            color: #0f172a;
        }}

        .trace-tip {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .trace-tip code {{
            background: #000;
            color: #38bdf8;
            padding: 2px 6px;
            border-radius: 4px;
        }}

        .stacktrace-details {{
            margin-top: 18px;
            border-top: 1px solid var(--border-color);
            padding-top: 14px;
        }}

        .stacktrace-details summary {{
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85rem;
            color: var(--text-muted);
            user-select: none;
        }}

        .stacktrace-details summary:hover {{
            color: var(--text-main);
        }}

        .stacktrace-code {{
            margin-top: 10px;
            background: #090d16;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 14px;
            font-family: Consolas, Monaco, "Courier New", monospace;
            font-size: 0.82rem;
            color: #cbd5e1;
            overflow-x: auto;
            max-height: 350px;
            white-space: pre-wrap;
        }}

        .success-banner {{
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 10px;
            padding: 40px;
            text-align: center;
        }}

        .success-banner h2 {{
            color: var(--color-success);
            font-size: 1.8rem;
            margin-bottom: 10px;
        }}

        .success-banner p {{
            color: #a7f3d0;
            font-size: 1.1rem;
        }}

        footer {{
            margin-top: 40px;
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="title-group">
                <h1>🐞 Přehled vad automatizovaných testů (Defect Report)</h1>
                <p>Generováno dovedností <code>bug-report</code> • Vyhodnocení stability a identifikace chyb</p>
            </div>
            <div class="env-badge-group">
                <div class="env-tag">🌐 Prostředí: <strong>{env_info['base_url']}</strong></div>
                <div class="env-tag">💻 OS: <strong>{env_info['os']}</strong></div>
                <div class="env-tag">🎭 Prohlížeč: <strong>{env_info['browser']}</strong></div>
                <div class="env-tag">🕒 Spuštěno: <strong>{env_info['timestamp']}</strong></div>
            </div>
        </header>

        <div class="kpi-grid">
            <div class="kpi-card kpi-total">
                <div class="kpi-value">{total_tests}</div>
                <div class="kpi-label">Celkem spuštěno testů</div>
            </div>
            <div class="kpi-card kpi-passed">
                <div class="kpi-value">{passed_tests}</div>
                <div class="kpi-label">Úspěšných testů</div>
            </div>
            <div class="kpi-card kpi-failed">
                <div class="kpi-value">{len(failures)}</div>
                <div class="kpi-label">Nalezených chyb</div>
            </div>
            <div class="kpi-card kpi-rate">
                <div class="kpi-value">{success_rate:.1f} %</div>
                <div class="kpi-label">Míra úspěšnosti (Pass Rate)</div>
            </div>
        </div>

        <div class="filter-bar">
            <div style="font-weight: 600; font-size: 0.9rem;">Filtrovat podle závažnosti:</div>
            <div class="filter-buttons">
                <button class="btn-filter active" onclick="filterDefects('all')">Všechny ({len(failures)})</button>
                <button class="btn-filter" onclick="filterDefects('blocker')">Blocker ({severity_counts['Blocker']})</button>
                <button class="btn-filter" onclick="filterDefects('critical')">Critical ({severity_counts['Critical']})</button>
                <button class="btn-filter" onclick="filterDefects('major')">Major ({severity_counts['Major']})</button>
                <button class="btn-filter" onclick="filterDefects('minor')">Minor ({severity_counts['Minor']})</button>
            </div>
        </div>

        <div class="defects-list" id="defectsList">
            {all_cards_str}
        </div>

        <footer>
            Vygenerováno automaticky systémem Antigravity AI Agent (Skill: <code>bug-report</code>) | Celková doba běhu testů: {duration:.2f} s
        </footer>
    </div>

    <script>
        function filterDefects(severity) {{
            const buttons = document.querySelectorAll('.btn-filter');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            const cards = document.querySelectorAll('.defect-card');
            cards.forEach(card => {{
                if (severity === 'all') {{
                    card.style.display = 'block';
                }} else {{
                    if (card.classList.contains('severity-' + severity)) {{
                        card.style.display = 'block';
                    }} else {{
                        card.style.display = 'none';
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ HTML Defect Report byl úspěšně vygenerován do: {output_html_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Spuštění testů, detekce vad a generování přehledného HTML Defect Reportu s důkazy."
    )
    parser.add_argument(
        "--test-path",
        default="tests",
        help="Cesta k testovací složce nebo konkrétnímu testu (výchozí: tests)."
    )
    parser.add_argument(
        "-k",
        dest="k_filter",
        default=None,
        help="Pytest filtr výrazů testů (např. -k 'create_course')."
    )
    parser.add_argument(
        "--output",
        default="docs/bug_report.html",
        help="Výstupní cesta pro HTML report (výchozí: docs/bug_report.html)."
    )
    parser.add_argument(
        "--evidence-dir",
        default="docs/evidence",
        help="Složka pro ukládání screenshotů a Playwright trace souborů (výchozí: docs/evidence)."
    )
    parser.add_argument(
        "--from-junit",
        default=None,
        help="Cesta k existujícímu JUnit XML reportu (přeskočí spouštění testů a vygeneruje report z dat)."
    )
    parser.add_argument(
        "--json-output",
        default=None,
        help="Volitelná cesta pro export seznamu vad do JSON formátu."
    )

    args = parser.parse_args()

    project_root = get_project_root()
    python_bin = get_python_executable(project_root)
    env_info = get_environment_info(project_root)

    print("=" * 80)
    print("AUTOMATIZOVANÉ GENEROVÁNÍ REPORTU VAD (SKILL: bug-report)")
    print("=" * 80)
    print(f"Kořenový adresář: {project_root}")
    print(f"Python interpreter: {python_bin}")
    if args.from_junit:
        print(f"Režim: Generování z existujícího JUnit reportu ({args.from_junit})")
    else:
        print(f"Testovací cíl: {args.test_path}")
        if args.k_filter:
            print(f"Filtr (-k): {args.k_filter}")
    print(f"Výstupní HTML: {args.output}")
    print(f"Evidence adresář: {args.evidence_dir}")
    print("-" * 80)

    # Označení aktivního běhu skillu pro kontrolní Stop hook
    marker_file = os.path.join(project_root, ".agents", "skills", "bug-report", ".last_run")
    try:
        os.makedirs(os.path.dirname(marker_file), exist_ok=True)
        with open(marker_file, "w", encoding="utf-8") as mf:
            json.dump({
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "test_path": args.test_path,
                "k_filter": args.k_filter
            }, mf, indent=2)
    except Exception:
        pass

    # 1. Spuštění testů a zachycení selhání
    total_tests, failures, duration = run_tests_and_collect_failures(
        project_root=project_root,
        python_bin=python_bin,
        test_path=args.test_path,
        k_filter=args.k_filter,
        evidence_dir=os.path.join(project_root, args.evidence_dir),
        from_junit=args.from_junit
    )

    # 2. Generování HTML reportu
    html_abs_path = os.path.join(project_root, args.output)
    generate_html_bug_report(
        output_html_path=html_abs_path,
        total_tests=total_tests,
        failures=failures,
        duration=duration,
        env_info=env_info,
        evidence_dir=os.path.join(project_root, args.evidence_dir)
    )

    # 3. Volitelný JSON export
    if args.json_output:
        json_abs_path = os.path.join(project_root, args.json_output)
        with open(json_abs_path, "w", encoding="utf-8") as jf:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": total_tests - len(failures),
                    "failed": len(failures),
                    "duration": duration,
                    "timestamp": env_info["timestamp"]
                },
                "defects": failures
            }, jf, ensure_ascii=False, indent=2)
        print(f"📄 JSON data uložena do: {json_abs_path}")

    # 4. Konzolový přehled
    print("\n" + "=" * 80)
    print(f"SOUHRN BĚHU: Spuštěno {total_tests} testů | Úspěšných: {total_tests - len(failures)} | Vad nalezeno: {len(failures)}")
    if failures:
        print("\nSEZNAM IDENTIFIKOVANÝCH VAD:")
        print(f"{'ID':<8} {'Závažnost':<10} {'US':<8} {'Test':<38} {'Důkaz'}")
        print("-" * 80)
        for d in failures:
            evidence_status = "📸 Snímek" if d["has_screenshot"] else "Bez důkazu"
            if d["has_trace"]:
                evidence_status += " + 🔍 Trace"
            print(f"{d['id']:<8} {d['severity']:<10} {d['user_story']:<8} {d['test_name'][:36]:<38} {evidence_status}")
    else:
        print("✅ Žádné vady nebyly zjištěny. Všechny testy jsou zelené.")
    print("=" * 80)


if __name__ == "__main__":
    main()
