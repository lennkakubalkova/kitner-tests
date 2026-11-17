# Automatizované testy – Portál Kitner & Demo Login (http://testovani.kitner.cz)

Sada automatizovaných E2E testů vytvořená v **Pythonu** pomocí **pytest** a **Playwright** pro aplikaci **Portál Kitner a Demo login** podle požadavků a akceptačních kritérií ze specifikace kurzu (*Specifikace požadavků podle zdrojového kódu (User Stories)*).

## Přehled projektu

- **Architektura:** Page Object Model (POM)
- **Lokátory:** Výhradně založeno na standardizovaných `data-test` a `data-testid` atributech
- **Framework:** pytest + Playwright
- **Reportování:** pytest-html (samostatný soubor `report.html`)
- **Celkem testů:** 34 testů pokrývajících všech 6 klíčových modulů aplikace:
  - **Modul 0 (Úvodní rozcestník - US-01):** 2 testy (`POR-01`, `POR-02`)
  - **Modul 1 (Autentizace, sezení, obnova hesla - US-02 až US-08):** 20 testů (`LOG-01` až `LOG-08`, `REG-01` až `REG-08`, `RST-01` až `RST-04`)
  - **Modul 2 & 4 (Katalog, detail, správa kurzů a běhů - US-09 až US-16):** 8 testů (`CRS-01` až `CRS-08`)
  - **Modul 3 (Moje kurzy - US-13):** 1 test (`MYC-01`)
  - **Modul 5 (Uživatelský profil a nástěnka - US-17, US-18):** 3 testy (`PRF-01` až `PRF-03`)
- **Úspěšnost:** 34 / 34 PASSED (100 %)

## Struktura souborů

```
├── pages/
│   ├── base_page.py          # Společná logika navigace a menu (navbar) s data-test lokátory
│   ├── portal_page.py        # Page Object pro úvodní rozcestník (US-01)
│   ├── login_page.py         # Page Object pro přihlášení (/login) s data-test lokátory
│   ├── register_page.py      # Page Object pro registraci (/register) s data-test lokátory
│   ├── forgot_password_page.py # Page Object pro obnovu hesla (/forgot-password)
│   ├── courses_page.py       # Page Object pro katalog kurzů a modály tvorby kurzu/iterace (/courses)
│   ├── course_detail_page.py # Page Object pro detail kurzu a termíny (/courses/{id})
│   ├── profile_page.py       # Page Object pro uživatelský profil (/profile)
│   ├── my_courses_page.py    # Page Object pro přehled mých kurzů (/my-courses)
│   └── home_page.py          # Page Object pro uvítací nástěnku uživatele (/home)
├── tests/
│   ├── conftest.py           # Fixtury Playwright, session autentizace a reálná registrace
│   ├── test_portal.py        # 2 testy úvodního rozcestníku (Modul 0)
│   ├── test_courses.py       # 8 testů katalogu, detailu kurzu, oprávnění lektora a tvorby kurzů/termínů
│   ├── test_login.py         # 8 testů přihlášení, odhlášení, normalizace emailu a autorizace
│   ├── test_registration.py  # 8 testů registrace, validací, normalizace a navigace
│   ├── test_forgot_password.py # 4 testy procesu obnovy hesla
│   ├── test_profile.py       # 3 testy uživatelského profilu (předvyplnění, editace IČO/telefonu, navigace)
│   └── test_my_courses.py    # 1 test přehledu zapsaných kurzů zákazníka
├── lokatory.md               # Kompletní přehled a tabulka všech data-test a data-testid lokátorů
├── kontroly_asserty.md       # Samostatný dokument s rozborem všech kontrol a jejich dostatečnosti
├── run_single_tests.py       # Skript pro sekvenční spuštění všech 34 testů po jednom s přehlednou tabulkou
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

# Spuštění celé sady testů (všech 34 testů)
py -m pytest

# Spuštění všech testů postupně po jednom s detailním souhrnem
py run_single_tests.py
```
