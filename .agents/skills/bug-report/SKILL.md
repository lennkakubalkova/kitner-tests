---
name: bug-report
description: Použij vždy, když uživatel chce spustit testy a reportovat chyby, nebo když agent autonomně provádí kontrolu regresí, identifikuje padající automatizované testy, analyzuje příčiny selhání, shromažďuje důkazy (screenshoty, traces) a generuje přehledný HTML/Markdown report nalezených chyb (Defect Report).
---

# Reportování chyb z automatizovaných testů (Defect Reporting)

Tento skill slouží k automatizovanému spouštění testů, detekci a analýze chyb, shromažďování průkazných materiálů (screenshoty, traces) a generování strukturovaného HTML reportu vad.

---

## 1. Co skill dělá

1. **Spuštění sady automatizovaných testů:**
   * Spouští testy přes `pytest` a `playwright`.
   * Lze spustit celou sadu nebo cílený testovací modul či filtr.
2. **Automatický záchyt důkazů při selhání:**
   * Při pádu testu fixture v `tests/conftest.py` automaticky pořídí **full-page screenshot** stavu stránky v okamžiku chyby.
   * Současně zaznamená a exportuje **Playwright Trace** (kompletní DOM snapshoty, síťové požadavky a akce konzole).
3. **Analýza vady a strukturovaný report:**
   Pro každý padající test skript zanalyzuje selhání a sestaví kompletní kartu vady obsahující:
   * **ID vady** (např. `BUG-01`, `BUG-02`).
   * **Závažnost (Severity):** `Blocker`, `Critical`, `Major`, `Minor`.
   * **Mapování na požadavky:** User Story (např. `US-14`) a Test Case (`TC-xx`).
   * **Kroky k reprodukci:** Přehledný číslovaný seznam kroků získaný ze struktury testu a docstringu.
   * **Očekávaný výsledek:** Co mělo nastat podle specifikace a aserce.
   * **Skutečný výsledek:** Reálné chování aplikace (přesná chybová zpráva, timeout nebo assertion error).
   * **Testovací prostředí:** Operační systém, prohlížeč, URL testovaného portálu, datum a čas běhu.
   * **Odkaz na důkaz (Evidence):** Odkaz na screenshot s náhledem přímo v reportu a odkaz na stažení Playwright trace.
   * **Technický stacktrace:** Rozbalovací blok s detailním výpisem pro vývojáře.
4. **Výstupní HTML přehled:**
   * Vygeneruje interaktivní dashboard s KPI kartami, filtry dle závažnosti a vizuálními kartami vad (`docs/bug_report.html`).

---

## 2. Spuštění generování reportu vad

Skript je umístěn ve složce `.agents/skills/bug-report/scripts/generate_bug_report.py`.

### Základní spuštění (všechny testy v projektu):
```bash
python .agents/skills/bug-report/scripts/generate_bug_report.py
```

### Spuštění konkrétního testovacího souboru:
```bash
python .agents/skills/bug-report/scripts/generate_bug_report.py --test-path tests/test_courses.py
```

### Spuštění testů podle klíčového slova (-k filtr):
```bash
python .agents/skills/bug-report/scripts/generate_bug_report.py -k "create_course"
```

### Volitelné parametry:
* `--test-path <cesta>`: Výchozí je `tests`. Lze zadat složku nebo soubor.
* `-k <filtr>`: Pytest výraz pro výběr konkrétních testů.
* `--output <cesta>`: Cesta k vygenerovanému HTML reportu (výchozí: `docs/bug_report.html`).
* `--evidence-dir <cesta>`: Složka pro ukládání screenshotů a traces (výchozí: `docs/evidence`).
* `--json-output <cesta>`: Export strukturovaných dat o vadách do JSON souboru pro integraci do CI/CD.

---

## 3. Struktura záznamu o chybě (Defect Card)

Každá zjištěná vada v reportu obsahuje:

| Položka | Popis | Příklad |
| :--- | :--- | :--- |
| **ID vady** | Jednoznačný identifikátor v rámci běhu | `BUG-01` |
| **Závažnost** | Kategorizace dopadu vady | `Critical` / `Major` |
| **User Story** | Vazba na byznysový požadavek | `US-14: Vytvoření nového kurzu lektorem` |
| **Test** | Soubor a název testovací metody | `tests/test_courses.py::test_lector_can_open_create_course_modal` |
| **Kroky k reprodukci** | Číslované kroky pro testery a vývojáře | 1. Přihlaš se jako lektor.<br>2. Otevři katalog kurzů.<br>3. Klikni na Přidat kurz. |
| **Očekávaný výsledek** | Správný stav aplikace | Modální okno pro vytvoření kurzu je zobrazeno a obsahuje formulářová pole. |
| **Skutečný výsledek** | Skutečný projev chyby | `Timeout 5000ms exceeded while waiting for element [data-test="modal_container"]` |
| **Prostředí** | Parametry testovacího běhu | Windows 11, Chromium (Headless), http://testovani.kitner.cz |
| **Důkaz (Screenshot)** | Snímek obrazovky v momentě selhání | Náhled obrázku s možností zvětšení |
| **Důkaz (Trace)** | Playwright trace soubor | `.zip` soubor pro otevření v `playwright show-trace` |

---

## 4. Pravidla projektu a čistota úložiště

* **Dodržení `AGENTS.md`:** Žádné skripty, logy ani reporty se neukládají volně do kořene projektu.
* **Verzované výstupy:** HTML report vad se ukládá do `docs/bug_report.html` a důkazy do `docs/evidence/` (nebo do ignorované složky `reports/`, pokud je to vyžádáno parametrem `--output`).
* **Automatické čištění trace:** Pokud test projde úspěšně, žádné zbytečné trace soubory se neukládají na disk, čímž se šetří místo i výkon.

---

## 5. Vynucení Definice hotovo (Stop Hook)

Systém využívá životní cyklus agenta a hook události `Stop` definovaný v `.agents/hooks.json`.
Hook spouští validační skript `.agents/skills/bug-report/scripts/verify_bug_report_dod.py`, který **nepustí agenta skončit (`decision: "continue"`)**, dokud nejsou stoprocentně splněny všechny 3 podmínky:

1. **Existuje HTML přehled:** Soubor `docs/bug_report.html` musí existovat a obsahovat vygenerovaný report.
2. **Report pro každý padající test:** Pro každý test, který v běhu selhal (zaznamenaný v JUnit XML), musí existovat odpovídající záznam (karta vady) v HTML reportu.
3. **Všechna povinná pole v každém reportu:** Každý záznam vady musí obsahovat:
   * Kroky k reprodukci (číslovaný seznam kroků),
   * Očekávaný výsledek,
   * Skutečný výsledek (chybová zpráva / aserce),
   * Testovací prostředí (OS, prohlížeč, URL portálu),
   * Odkaz na existující důkaz (screenshot `.png` nebo trace `.zip` soubor v `docs/evidence/`).

