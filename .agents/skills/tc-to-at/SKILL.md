---
name: tc-to-at
description: Použij vždy, když máš schválené manuální test casy a chceš z nich vytvořit nebo upravit automatizované testy v Playwrightu a pytestu podle architektury projektu.
---

# Pracovní postup: Převod Test Casů na automatizované testy (TC -> AT)

Tento skill definuje standardizovaný 5krokový proces, kterým agent přetváří schválené manuální test casy na plně automatizované testy rozdělené do 5vrstvé architektury projektu, a ověřuje jejich kvalitu pomocí skriptu „Definice hotovo“.

---

## Přehled fází pracovního postupu

| Krok | Název kroku | Kdo ho dělá | Vstup | Výstup |
| :---: | :--- | :---: | :--- | :--- |
| **1.** | **Příprava vstupů** | **Vy + Agent** | Schválené manuální test casy (`TC_*.md`), `AGENTS.md` | Mapování kroků na 5 vrstev projektu (`data/`, `pages/`, `tests/`) |
| **2.** | **Generování a implementace testů** | **Agent** | Schválené zadání | Kód v příslušných vrstvách (`data/test_data.py`, `pages/`, `tests/`) |
| **3.** | **Review lokátorů a assertů** | **Vy + Agent** | Vygenerovaný kód | Kontrola dodržení skillu `kitner-locators` a `AGENTS.md` |
| **4.** | **Spuštění skriptu „Definice hotovo“** | **Agent** | Cesta k TC a testovacímu souboru | Výsledek kontroly kvality a stability (3× zelený běh) |
| **5.** | **Merge a uložení do Gitu** | **Agent / Vy** | Schválené a ověřené testy | Git commit a push do repozitáře |

---

## Detailní popis jednotlivých kroků

### Krok 1: Příprava vstupů
* **Kdo:** Uživatel předá test casy, Agent zanalyzuje vstupy a projekt.
* **Vstup:** Markdown soubor se schválenými test casy (např. `docs/testcases/TC_US04_zapis_na_kurz.md`).
* **Činnost agenta:**
  1. Identifikuje všechny test casy (`TC-01`, `TC-02`...) a jejich kroky.
  2. Zkontroluje existující Page Objecty v `pages/`, zda již obsahují potřebné lokátory a metody.
  3. Identifikuje nová testovací data, která je třeba doplnit do `data/test_data.py`.
  4. Určí cílový testovací soubor v `tests/test_*.py`.
* **Výstup:** Plán implementace rozdělený do vrstev `data`, `pages` a `tests`.

---

### Krok 2: Generování a implementace testů
* **Kdo:** Agent.
* **Vstup:** Schválené vstupy a test casy.
* **Pravidla implementace:**
  1. **Vrstva `data/`:** Všechny vstupy (jména, telefony, IČO, chybové hlášky) definuj v `data/test_data.py`.
  2. **Vrstva `pages/`:** Veškeré selektory a interakce (vyplnění, kliknutí, odeslání) zapouzdři do metod příslušného Page Objectu.
  3. **Vrstva `tests/`:** Testovací funkce obsahují výhradně volání Page Object metod a Playwright web-first aserce (`expect(...)`). Každý test v docstringu uvádí ID manuálního test casu (např. `TC-01`).
* **Přísné zákazy:**
  * Žádné volání `page.locator(...)` přímo v testech.
  * Zákaz pevných čekání `time.sleep()` a `wait_for_timeout()`.
  * Zákaz simulace serverových odpovědí (`page.route()`) – testy musí volat reálné prostředí.
  * Žádné XPath ani selektory mimo `data-test` / `data-testid`.
* **Výstup:** Nový nebo rozšířený kód v souborech projektu.

---

### Krok 3: Review lokátorů a assertů
* **Kdo:** Uživatel (Tester) + Agent.
* **Vstup:** Implementovaný kód.
* **Činnost:**
  * Zkontroluje se dodržení pravidel skillu `kitner-locators` (pouze `data-test` a `data-testid`).
  * Zkontroluje se, zda aserce ověřují skutečné stavy aplikace bez podmíněného větvení (`if/else assert`).
* **Výstup:** Kód schválený k automatickému ověření.

---

### Krok 4: Skript „Definice hotovo“ (Definition of Done)
* **Kdo:** Agent.
* **Vstup:** Cesta k souboru s manuálními test casy a cesta k testovacímu souboru pytestu.
* **Činnost agenta:**
  Spustí validační skript ze složky skillu:
  ```bash
  python .agents/skills/tc-to-at/scripts/verify_automated_tests.py --tc-file <cesta_k_tc.md> --test-file <cesta_k_testu.py>
  ```
* **Kritéria, která skript automaticky ověřuje:**
  1. **100% pokrytí TC:** Každé ID test casu z manuálního dokumentu (`TC-01`, `TC-02`...) má svůj test v testovacím souboru.
  2. **Zákaz pevných čekání:** Statická analýza kódu ověří absenci `time.sleep` a `wait_for_timeout`.
  3. **Žádné přímé lokátory v testech:** Ověří, že testovací soubor nevolá `page.locator(` ani `page.get_by_`.
  4. **Zákaz mockování odpovědí:** Ověří absenci `page.route` pro simulaci výsledků.
  5. **Stabilita (Flakiness test):** Spustí pytest **3× po sobě**. Všechny 3 běhy musí projít na 100 % (PASS).
* **Výstup:** Výsledek `✅ PASS` nebo `❌ FAIL`.

---

### Krok 5: Merge a uložení do Gitu
* **Kdo:** Agent (po schválení).
* **Vstup:** Všechny ověřené změny se statusem PASS.
* **Činnost:** Provede Git commit a push do vzdáleného repozitáře.
* **Výstup:** Čistý Git pracovní strom a aktualizovaný repozitář na GitHubu.
