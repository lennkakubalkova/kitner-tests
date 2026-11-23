# Pokyny pro AI Agenty (AGENTS.md)

Tento soubor definuje architekturu, pravidla a postupy pro vývoj a údržbu automatizovaných testů v tomto projektu. Pravidla zde uvedená jsou trvale závazná pro všechny úkoly.

---

## 1. Architektura projektu (5 vrstev)

Projekt je striktně rozdělen do 5 vrstev. Všechny nově vytvářené soubory musí být umístěny do příslušného adresáře:

1. **`config/` (Konfigurace)**
   * Nastavení testovacího prostředí, URL adresy, přepínače prohlížeče (headless/headed), timeouty.
   * Příklad: `config/config.py`.

2. **`data/` (Testovací data)**
   * Všechna statická i dynamická testovací data, přihlašovací údaje, parametry kurzů, chybové hlášky.
   * V testech se data nepíší natvrdo, vždy se importují z této složky.
   * Příklad: `data/test_data.py`.

3. **`pages/` (Page Object Model)**
   * Třídy reprezentující jednotlivé webové stránky a komponenty portálu.
   * Zapouzdřují lokátory prvků a metody pro interakci se stránkou.
   * Příklad: `pages/base_page.py`, `pages/login_page.py`, `pages/courses_page.py`.

4. **`tests/` (Testovací scénáře)**
   * Soubory s testy (`test_*.py`) a sdílené fixtures (`conftest.py`).
   * Testy obsahují pouze volání metod Page Objectů a aserce.
   * Příklad: `tests/test_login.py`, `tests/test_courses.py`.

5. **`utils/` (Pomocné nástroje a skripty)**
   * Pomocné funkce, generátory dat, pomocné runner skripty a obslužné utility (např. odesílání reportů e-mailem, hromadné zakládání uživatelů přes API).
   * Příklad: `utils/helpers.py`.

### Pravidlo pro kořenový adresář:
V kořenovém adresáři se smí nacházet **pouze globální konfigurační a projektové soubory**:
* `pytest.ini`, `pyproject.toml`, `.gitignore`, `README.md`, `AGENTS.md`, `lokatory.md`.
* **Žádné skripty, testy ani data se nesmí nacházet volně v kořeni projektu.**

---

## 2. Přísná pravidla projektu (Co se nesmí)

1. **Žádné přímé lokátory v testech:**
   * V souborech ve složce `tests/` je zakázáno volat `page.locator(...)`, `page.get_by_*` apod. Všechny lokátory musí být definovány jako atributy nebo metody v příslušném Page Objectu v `pages/`.
2. **Pravidla pro selektory (viz skill `kitner-locators`):**
   * Používej **výhradně** atributy `data-test` a `data-testid`.
   * Nikdy nepoužívej XPath, křehké CSS selektory (`div > div:nth-child(2)`) ani selektory závislé na vizuálním stylu.
   * **STOP pravidlo:** Pokud prvek nemá `data-test`, nepoužívej alternativní selektor, ale zastav se a požádej o doplnění atributu do aplikace.
3. **Zákaz fixních čekání:**
   * Nikdy nepoužívej `time.sleep()` ani `page.wait_for_timeout()`.
   * Používej automatické čekání Playwrightu a web-first aserce (`expect(locator).to_be_visible()`, `wait_for_load_state()`).
4. **Žádné podmíněné kontroly v testech:**
   * V testech nepoužívej `if ...: assert ... else: assert ...`. Každý testovací krok musí mít jednoznačnou aserci.

---

## 3. Spouštění testů

Projekt využívá Python 3.13, `pytest` a `playwright`.

* **Spuštění všech testů:**
  ```bash
  pytest
  ```
* **Spuštění konkrétního testovacího souboru:**
  ```bash
  pytest tests/test_login.py
  ```
* **Spuštění konkrétního testu:**
  ```bash
  pytest tests/test_login.py -k "test_login_success"
  ```
* **Generování HTML reportu:**
  ```bash
  pytest --html=report.html --self-contained-html
  ```
