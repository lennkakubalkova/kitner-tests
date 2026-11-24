#!/usr/bin/env python3
"""
Skript: generate_coverage_report.py
Účel: Skript pro skill coverage-report.
Prochází projekt (testy, manuální test casy a definice User Stories)
a generuje přehledný, opakovatelný HTML report a souhrn pokrytí.
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime

# Definice oficiálních User Stories projektu Kitner
PROJECT_USER_STORIES = [
    {
        "id": "US-01",
        "alias": ["US01"],
        "title": "Úvodní navigační rozcestník portálu",
        "module": "Modul 0: Portál a rozcestník",
        "description": "Jako návštěvník chci přehledný rozcestník s odkazy na jednotlivé demo aplikace, abych se mohl snadno zorientovat a přejít k testování."
    },
    {
        "id": "US-02",
        "alias": ["US01-REG", "US01_REG"],
        "title": "Registrace zákaznického účtu a validace",
        "module": "Modul 1: Autentizace",
        "description": "Jako nový uživatel se chci zaregistrovat pomocí jména, emailu a hesla, aby mi systém vytvořil bezpečný profil a ověřil unikátnost emailu."
    },
    {
        "id": "US-03",
        "alias": ["US02-LOG"],
        "title": "Přihlašování uživatelů a autorizace rolí",
        "module": "Modul 1: Autentizace",
        "description": "Jako registrovaný uživatel nebo lektor se chci přihlásit do aplikace, abych získal přístup k funkcím podle své role."
    },
    {
        "id": "US-04",
        "alias": ["US02-LGT"],
        "title": "Odhlášení ze systému a ukončení sezení",
        "module": "Modul 1: Autentizace",
        "description": "Jako přihlášený uživatel se chci kdykoliv bezpečně odhlásit, aby bylo mé sezení ukončeno a privátní ovládací prvky skryty."
    },
    {
        "id": "US-05",
        "alias": [],
        "title": "Obnova zapomenutého hesla",
        "module": "Modul 1: Autentizace",
        "description": "Jako uživatel chci požádat o resetovací odkaz na email v případě zapomenutého hesla, abych mohl obnovit přístup k účtu."
    },
    {
        "id": "US-09",
        "alias": [],
        "title": "Veřejný přehled a katalog kurzů",
        "module": "Modul 2: Katalog kurzů",
        "description": "Jako anonymní návštěvník chci vidět seznam všech nabízených kurzů včetně cen a kapacit bez nutnosti přihlášení."
    },
    {
        "id": "US-10",
        "alias": [],
        "title": "Zobrazení detailu kurzu a termínů",
        "module": "Modul 2: Katalog kurzů",
        "description": "Jako zájemce o kurz chci zobrazit podrobné informace o osnově a vypsaných termínech, abych si mohl vybrat termín konání."
    },
    {
        "id": "US-11",
        "alias": ["US03"],
        "title": "Vyhledávání a filtrování kurzů dle kapacity",
        "module": "Modul 2: Katalog kurzů",
        "description": "Jako zájemce chci vyhledávat kurzy podle názvu a filtrovat je podle volné kapacity, abych rychle našel kurz s volnými místy."
    },
    {
        "id": "US-12",
        "alias": ["US04"],
        "title": "Zápis studenta na vypsaný termín kurzu",
        "module": "Modul 4: Zápis na kurzy",
        "description": "Jako student se chci přihlásit na volný termín kurzu vyplněním telefonu a IČO, abych si zajistil místo na školení."
    },
    {
        "id": "US-13",
        "alias": [],
        "title": "Přehled zapsaných kurzů (Moje kurzy)",
        "module": "Modul 3: Zákaznická zóna",
        "description": "Jako přihlášený student chci mít přehled svých zapsaných kurzů na stránce Moje kurzy, abych viděl termíny svých akcí."
    },
    {
        "id": "US-14",
        "alias": [],
        "title": "Vytvoření nového kurzu lektorem",
        "module": "Modul 2: Správa kurzů",
        "description": "Jako lektor chci zakládat nové vzdělávací kurzy s názvem, popisem, kapacitou a cenou, abych rozšířil nabídku školení."
    },
    {
        "id": "US-15",
        "alias": ["US05"],
        "title": "Vypsání termínu (iterace) kurzu lektorem",
        "module": "Modul 2: Správa kurzů",
        "description": "Jako lektor chci k existujícímu kurzu vypsat nový termín (datum, den, čas, místo), aby se na něj mohli studenti registrovat."
    },
    {
        "id": "US-16",
        "alias": [],
        "title": "Zobrazení přihlášených účastníků pro lektora",
        "module": "Modul 2: Správa kurzů",
        "description": "Jako lektor chci vidět seznam přihlášených studentů na mých kurzech, abych měl přehled o obsazenosti a účastnících."
    },
    {
        "id": "US-17",
        "alias": [],
        "title": "Personalizované uvítání nového uživatele",
        "module": "Modul 5: Uživatelská zóna",
        "description": "Jako nově registrovaný uživatel chci po prvním přihlášení vidět uvítací hlášku se svým jménem pro potvrzení identity."
    },
    {
        "id": "US-18",
        "alias": [],
        "title": "Uživatelský profil a správa údajů",
        "module": "Modul 5: Uživatelská zóna",
        "description": "Jako přihlášený uživatel chci v sekci Můj Profil vidět své údaje a mít možnost aktualizovat telefon a IČO."
    },
    {
        "id": "US-19",
        "alias": [],
        "title": "Globální navigace a autorizační hranice",
        "module": "Modul 0: Společné komponenty",
        "description": "Jako uživatel chci funkční navigační lištu s jasným rozlišením dostupných odkazů podle přihlášeného stavu a role."
    }
]

def read_file_safe(filepath: str) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1250", "windows-1250", "latin1"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""

def scan_manual_test_cases(docs_dir: str) -> dict:
    """Scans docs/testcases directory and counts manual TCs per User Story."""
    tc_counts = {}
    if not os.path.exists(docs_dir):
        return tc_counts

    for root, _, files in os.walk(docs_dir):
        for f in files:
            if f.endswith(".md"):
                fpath = os.path.join(root, f)
                content = read_file_safe(fpath)
                
                # Hledáme US v názvu souboru nebo obsahu
                us_in_file = re.findall(r"\bUS[-_]?(\d+)\b", f + " " + content, re.IGNORECASE)
                tc_items = re.findall(r"(?m)^#{2,4}\s+TC[-_]?\d+", content)
                count = len(tc_items)
                
                for us_num in set(us_in_file):
                    us_id = f"US-{int(us_num):02d}"
                    tc_counts[us_id] = tc_counts.get(us_id, 0) + count

    return tc_counts

def scan_automated_tests(tests_dir: str) -> dict:
    """Scans tests directory and maps automated test functions to User Stories."""
    at_mapping = {}

    if not os.path.exists(tests_dir):
        return at_mapping

    for f in os.listdir(tests_dir):
        if f.startswith("test_") and f.endswith(".py"):
            fpath = os.path.join(tests_dir, f)
            content = read_file_safe(fpath)

            # Rozdělení na jednotlivé testovací funkce
            # Hledáme def test_...(self, ...) nebo def test_...(...)
            test_funcs = re.split(r"(?m)^(?:\s{4}|\s{0})def\s+(test_\w+)\s*\(", content)
            
            # První část je hlavička souboru
            file_header = test_funcs[0]
            header_us = re.findall(r"\bUS[-_]?(\d+)\b", file_header, re.IGNORECASE)

            for i in range(1, len(test_funcs), 2):
                func_name = test_funcs[i]
                func_body = test_funcs[i+1] if i+1 < len(test_funcs) else ""
                
                # Hledáme US zmínky v těle/docstringu testu
                us_in_test = re.findall(r"\bUS[-_]?(\d+)\b", func_body[:800], re.IGNORECASE)
                
                assigned_us = set()
                if us_in_test:
                    for num in us_in_test:
                        assigned_us.add(f"US-{int(num):02d}")
                elif header_us:
                    for num in header_us:
                        assigned_us.add(f"US-{int(num):02d}")
                else:
                    # Heuristické mapování podle názvu souboru
                    if "registration" in f:
                        assigned_us.add("US-02")
                    elif "login" in f:
                        assigned_us.add("US-03")
                    elif "logout" in f:
                        assigned_us.add("US-04")
                    elif "forgot_password" in f:
                        assigned_us.add("US-05")
                    elif "portal" in f:
                        assigned_us.add("US-01")
                    elif "profile" in f:
                        assigned_us.add("US-18")
                    elif "my_courses" in f:
                        assigned_us.add("US-13")
                    elif "navigation" in f:
                        assigned_us.add("US-19")
                    elif "courses" in f:
                        assigned_us.add("US-09")

                for u_id in assigned_us:
                    if u_id not in at_mapping:
                        at_mapping[u_id] = []
                    at_mapping[u_id].append({
                        "file": f,
                        "function": func_name
                    })

    return at_mapping

def generate_html_report(us_data: list, summary: dict, output_path: str):
    """Generates a modern, clean HTML coverage report."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    rows_html = []
    for item in us_data:
        status_badge = ""
        if item["status"] == "POKRYTO":
            status_badge = '<span class="badge badge-success">🟢 POKRYTO</span>'
        elif item["status"] == "POUZE MANUÁLNÍ":
            status_badge = '<span class="badge badge-warning">🟡 POUZE MANUÁLNÍ TC</span>'
        else:
            status_badge = '<span class="badge badge-danger">🔴 NEPOKRYTO</span>'

        test_list_html = ""
        if item["automated_tests"]:
            test_items = "".join([f'<li><code>{t["file"]}::{t["function"]}</code></li>' for t in item["automated_tests"]])
            test_list_html = f'<details><summary>Zobrazit testy ({len(item["automated_tests"])})</summary><ul class="test-list">{test_items}</ul></details>'
        else:
            test_list_html = '<span class="text-muted">Žádný automatizovaný test</span>'

        row = f"""
        <tr>
            <td class="font-bold">{item["id"]}</td>
            <td>
                <div class="font-semibold">{item["title"]}</div>
                <div class="text-sm text-muted">{item["description"]}</div>
            </td>
            <td><span class="module-tag">{item["module"]}</span></td>
            <td class="text-center font-bold">{item["manual_tc_count"]}</td>
            <td class="text-center font-bold text-primary">{item["at_count"]}</td>
            <td>{status_badge}</td>
            <td>{test_list_html}</td>
        </tr>
        """
        rows_html.append(row)

    coverage_pct = summary["coverage_percent"]
    bar_color = "#10b981" if coverage_pct >= 90 else "#f59e0b" if coverage_pct >= 60 else "#ef4444"

    html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Přehled pokrytí User Stories automatizovanými testy</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 24px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 28px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 26px; }}
        .header p {{ margin: 0; opacity: 0.9; font-size: 14px; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
        }}
        .kpi-label {{ font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 6px; }}
        .kpi-value {{ font-size: 28px; font-weight: 700; color: #0f172a; }}
        .progress-bar-container {{
            background: #e2e8f0;
            border-radius: 9999px;
            height: 10px;
            margin-top: 10px;
            overflow: hidden;
        }}
        .progress-bar {{
            height: 100%;
            background: {bar_color};
            width: {coverage_pct}%;
            transition: width 0.3s ease;
        }}
        .table-card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            overflow: hidden;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }}
        th {{
            background-color: #f1f5f9;
            padding: 14px 16px;
            font-weight: 600;
            color: #475569;
            border-bottom: 1px solid #cbd5e1;
        }}
        td {{
            padding: 14px 16px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: top;
        }}
        tr:hover {{ background-color: #f8fafc; }}
        .font-bold {{ font-weight: 700; }}
        .font-semibold {{ font-weight: 600; }}
        .text-sm {{ font-size: 12px; }}
        .text-muted {{ color: #64748b; }}
        .text-center {{ text-align: center; }}
        .text-primary {{ color: #2563eb; }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
        }}
        .badge-success {{ background-color: #dcfce7; color: #15803d; }}
        .badge-warning {{ background-color: #fef3c7; color: #b45309; }}
        .badge-danger {{ background-color: #fee2e2; color: #b91c1c; }}
        .module-tag {{
            display: inline-block;
            background: #f1f5f9;
            color: #475569;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        details summary {{
            cursor: pointer;
            color: #2563eb;
            font-weight: 600;
            outline: none;
        }}
        .test-list {{
            margin: 8px 0 0 0;
            padding-left: 20px;
            font-size: 12px;
            color: #334155;
        }}
        .test-list li {{ margin-bottom: 4px; }}
        code {{
            background: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: Consolas, Monaco, monospace;
            font-size: 11px;
        }}
        .footer {{
            text-align: center;
            margin-top: 24px;
            font-size: 13px;
            color: #94a3b8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Matice pokrytí User Stories automatizovanými testy</h1>
            <p>Projekt: <strong>Kitner Testování (Demo Login)</strong> | Vygenerováno: <strong>{datetime.now().strftime("%d.%m.%Y v %H:%M:%S")}</strong></p>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Celkové pokrytí US</div>
                <div class="kpi-value">{coverage_pct:.1f} %</div>
                <div class="progress-bar-container">
                    <div class="progress-bar"></div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Pokryté User Stories</div>
                <div class="kpi-value">{summary["covered_us_count"]} / {summary["total_us_count"]}</div>
                <div class="text-sm text-muted" style="margin-top: 6px;">{summary["total_us_count"] - summary["covered_us_count"]} zbývá pokrýt</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Celkem automatizovaných testů</div>
                <div class="kpi-value text-primary">{summary["total_at_count"]}</div>
                <div class="text-sm text-muted" style="margin-top: 6px;">Spouštěno přes pytest</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Zpracované manuální TC</div>
                <div class="kpi-value">{summary["total_manual_tc_count"]}</div>
                <div class="text-sm text-muted" style="margin-top: 6px;">V adresáři docs/testcases/</div>
            </div>
        </div>

        <div class="table-card">
            <table>
                <thead>
                    <tr>
                        <th style="width: 80px;">ID</th>
                        <th>Název a popis User Story</th>
                        <th>Modul</th>
                        <th style="width: 100px; text-align: center;">Manuální TC</th>
                        <th style="width: 100px; text-align: center;">Automat. testy</th>
                        <th style="width: 150px;">Stav pokrytí</th>
                        <th>Seznam přiřazených testů</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows_html)}
                </tbody>
            </table>
        </div>

        <div class="footer">
            Automaticky vygenerováno skillem <strong>coverage-report</strong> | Testovací framework: pytest + Playwright
        </div>
    </div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    parser = argparse.ArgumentParser(description="Generátor přehledu pokrytí User Stories automatizovanými testy.")
    parser.add_argument("--output", default="reports/coverage_report.html", help="Cesta k výstupnímu HTML souboru")
    args = parser.parse_args()

    project_root = os.getcwd()
    tests_dir = os.path.join(project_root, "tests")
    docs_dir = os.path.join(project_root, "docs", "testcases")

    print("=" * 80)
    print("ANALÝZA POKRYTÍ USER STORIES TESTY (SKILL: coverage-report)")
    print("=" * 80)

    # 1. Skenování manuálních TC a automatizovaných testů
    manual_tc_map = scan_manual_test_cases(docs_dir)
    automated_test_map = scan_automated_tests(tests_dir)

    # 2. Sestavení dat pro každou User Story
    table_data = []
    covered_us = 0
    total_manual_tc = sum(manual_tc_map.values())
    all_assigned_tests = set()

    for us in PROJECT_USER_STORIES:
        u_id = us["id"]
        
        # Manuální TC pro tuto US
        m_count = manual_tc_map.get(u_id, 0)
        
        # Automatizované testy pro tuto US
        at_tests = automated_test_map.get(u_id, [])
        for a in at_tests:
            all_assigned_tests.add(f"{a['file']}::{a['function']}")

        at_count = len(at_tests)

        if at_count > 0:
            status = "POKRYTO"
            covered_us += 1
        elif m_count > 0:
            status = "POUZE MANUÁLNÍ"
        else:
            status = "NEPOKRYTO"

        table_data.append({
            "id": u_id,
            "title": us["title"],
            "module": us["module"],
            "description": us["description"],
            "manual_tc_count": m_count,
            "at_count": at_count,
            "automated_tests": at_tests,
            "status": status
        })

    total_us = len(PROJECT_USER_STORIES)
    coverage_pct = (covered_us / total_us * 100) if total_us > 0 else 0
    total_at_count = len(all_assigned_tests)

    summary = {
        "total_us_count": total_us,
        "covered_us_count": covered_us,
        "coverage_percent": coverage_pct,
        "total_at_count": total_at_count,
        "total_manual_tc_count": total_manual_tc
    }

    # 3. Výpis tabulky do konzole
    print(f"{'ID':<7} {'Stav':<12} {'Manuální TC':<12} {'AT Počet':<10} {'User Story Název'}")
    print("-" * 80)
    for item in table_data:
        status_icon = "🟢 POKRYTO" if item["status"] == "POKRYTO" else "🟡 POUZE TC" if item["status"] == "POUZE MANUÁLNÍ" else "🔴 NEPOKRYTO"
        print(f"{item['id']:<7} {status_icon:<12} {item['manual_tc_count']:<12} {item['at_count']:<10} {item['title']}")
    print("-" * 80)
    print(f"CELKEM: {covered_us}/{total_us} User Stories pokryto ({coverage_pct:.1f} %)")
    print(f"POČET AUTOMATIZOVANÝCH TESTŮ: {total_at_count} | MANUÁLNÍCH TC: {total_manual_tc}")
    print("=" * 80)

    # 4. Uložení HTML reportu
    output_abs = os.path.abspath(args.output)
    generate_html_report(table_data, summary, output_abs)
    print(f"\n✅ HTML report byl úspěšně vygenerován do: {output_abs}")

if __name__ == "__main__":
    main()
