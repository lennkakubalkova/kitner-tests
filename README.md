# Automatizované testy – Demo Login (http://testovani.kitner.cz)

Sada automatizovaných E2E testů vytvořená v **Pythonu** pomocí **pytest** a **Playwright** pro aplikaci **Demo login**.

## Přehled projektu

- **Architektura:** Page Object Model (POM)
- **Framework:** pytest + Playwright
- **Reportování:** pytest-html (samostatný soubor `report.html`)
- **Celkem testů:** 14 (7 pro Registraci, 7 pro Login a Sezení)
- **Úspěšnost:** 14 / 14 PASSED (100 %)

## Struktura souborů

```
├── pages/
│   ├── base_page.py          # Společná logika navigace a menu (navbar)
│   ├── login_page.py         # Page Object pro přihlášení (/login)
│   ├── register_page.py      # Page Object pro registraci (/register)
│   ├── courses_page.py       # Page Object pro přehled kurzů (/courses)
│   └── home_page.py          # Page Object pro nástěnku uživatele (/home)
├── tests/
│   ├── conftest.py           # Fixtury Playwright, session autentizace a reálná registrace
│   ├── test_login.py         # 7 testů přihlášení, odhlášení a autorizace
│   └── test_registration.py  # 7 testů registrace, validací a navigace
├── kontroly_asserty.md       # Samostatný dokument s rozborem všech kontrol a jejich dostatečnosti
├── pytest.ini                # Konfigurace spouštění testů a generování HTML reportu
├── send_report_email.py      # Skript pro odeslání HTML reportu na email
├── report.html               # Vygenerovaný detailní interaktivní HTML report
└── README.md                 # Dokumentace projektu
```

## Spuštění testů

```powershell
# Instalace závislostí
py -m pip install playwright pytest pytest-html
py -m playwright install chromium

# Spuštění celé sady testů
py -m pytest

# Odeslání reportu na email (při nastavených proměnných prostředí)
$env:SMTP_HOST="smtp.vas-server.cz"
$env:SMTP_PORT="587"
$env:SMTP_USER="uzivatel@domena.cz"
$env:SMTP_PASS="tajne_heslo"
py send_report_email.py
```

