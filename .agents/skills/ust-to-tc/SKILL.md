---
name: ust-to-tc
description: Použij vždy, když uživatel zadá User Story, požadavek nebo zadání, nebo když agent při práci s User Stories autonomně analyzuje akceptační kritéria, navrhuje manuální test casy či doplňuje chybějící testovací scénáře pro nepokryté požadavky.
---

# Pracovní postup: Převod User Story na manuální Test Casy (UST -> TC)

Tento skill definuje standardizovaný 4krokový postup, kterým agent přetváří zadání User Story na strukturované, kvalitní manuální test casy, a ověřuje jejich kompletnost pomocí automatického skriptu „Definice hotovo“.

---

## Přehled fází pracovního postupu

| Krok | Název kroku | Kdo ho dělá | Vstup | Výstup |
| :---: | :--- | :---: | :--- | :--- |
| **1.** | **Review User Story** | **Vy + Agent** | Text User Story od uživatele | Očíslovaná akceptační kritéria (`AC1`, `AC2`...) a ujasněné nejasnosti |
| **2.** | **Návrh test casů agentem** | **Agent** | Schválená AC | Markdown soubor s test casy dle předepsané struktury |
| **3.** | **Uživatelské review** | **Vy (Tester)** | Vygenerované test casy | Zpětná vazba / Schválení návrhu |
| **4.** | **Spuštění skriptu „Hotovo“** | **Agent** | Soubor s test casy | Výsledek validace (`PASS / FAIL`) ze skriptu |

---

## Detailní popis jednotlivých kroků

### Krok 1: Review User Story
* **Kdo:** Uživatel zadá text, Agent zanalyzuje.
* **Vstup:** Uživatelské zadání (např. *„Jako uživatel chci... aby... Akceptační kritéria: 1. ..., 2. ...“*).
* **Činnost agenta:**
  1. Zkontroluje srozumitelnost, jednoznačnost a testovatelnost požadavku.
  2. Převede akceptační kritéria do přehledného očíslovaného seznamu (`AC1: ...`, `AC2: ...`).
  3. Pokud v zadání chybí klíčové informace (např. chybové stavy, formáty polí, oprávnění), **zastaví se a položí doplňující otázky**.
* **Výstup:** Odsouhlasený seznam akceptačních kritérií.

---

### Krok 2: Návrh test casů agentem
* **Kdo:** Agent.
* **Vstup:** Zanalyzovaná a očíslovaná akceptační kritéria.
* **Činnost agenta:**
  Pro každé akceptační kritérium navrhne:
  * **Pozitivní test casy** (Happy path – ověření správného fungování).
  * **Negativní test casy** (Validace, chybové vstupy, odmítnutí neplatných dat).
  * **Hraniční test casy** (Mezní hodnoty, maximální/minimální délky, práva rolí).
* **Povinná struktura každého Test Casu:**
  Každý test case musí mít tuto pevnou strukturu v Markdownu:
  ```markdown
  ### TC-01: Název testovacího případu
  * **Pokrytá kritéria:** AC1
  * **Typ testu:** Pozitivní / Negativní / Hraniční
  * **Předpoklady (Preconditions):** Výchozí stav systému a uživatele.
  * **Kroky testu (Steps):**
    1. První krok.
    2. Druhý krok.
    3. Třetí krok.
  * **Očekávaný výsledek (Expected Result):** Jednoznačně definovaný výstup.
  ```
* **Výstup:** Soubor s test casy (např. uložený v `docs/testcases/TC_<nazev_story>.md`).

---

### Krok 3: Vaše review test casů
* **Kdo:** Uživatel (Tester / QA).
* **Vstup:** Navržené test casy.
* **Činnost:**
  * Uživatel test casy zkontroluje z pohledu doménové logiky a reálného provozu.
  * Vznese případné připomínky k doplnění scénářů nebo změně kroků.
  * Agent zapracuje úpravy a vygeneruje aktualizovanou verzi.
* **Výstup:** Schválený obsah test casů uživatelem.

---

### Krok 4: Skript „Definice hotovo“ (Definition of Done)
* **Kdo:** Agent (spustí skript).
* **Vstup:** Cesta k Markdown souboru s test casy.
* **Činnost agenta:**
  Spustí validační skript ze složky skillu:
  ```bash
  python .agents/skills/ust-to-tc/scripts/verify_testcases.py <cesta_k_souboru_s_testy.md>
  ```
* **Kritéria, která skript striktně kontroluje:**
  1. **100% pokrytí AC:** Každé nalezené `AC` musí mít přiřazený minimálně 1 test case.
  2. **Kompletnost TC:** Každý test case musí obsahovat:
     * Unikátní ID (`TC-xx`) a název.
     * Vazbu na kritérium (`Pokrytá kritéria: AC...`).
     * Vyplněné předpoklady (`Předpoklady:` / `Preconditions:`).
     * Vyplněné očíslované kroky (`Kroky:` / `Steps:`).
     * Jednoznačný očekávaný výsledek (`Očekávaný výsledek:` / `Expected Result:`).
  3. **Čistota výstupu:** Žádné nevyplněné položky ani zástupné texty (`TODO`, `TBD`, `???`, `[Doplňte]`).
* **Výstup:**
  * Pokud skript vrátí **PASS** (návratový kód 0), úkol je splněn a hotov.
  * Pokud skript vrátí **FAIL** (návratový kód 1), agent musí nedostatky neprodleně opravit a skript spustit znovu.
