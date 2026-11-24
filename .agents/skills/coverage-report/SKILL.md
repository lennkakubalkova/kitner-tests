---
name: coverage-report
description: Použij vždy, když uživatel chce zobrazit nebo vygenerovat přehled pokrytí User Stories testy, zjistit stav automatizace projektu nebo vygenerovat HTML report matice sledovatelnosti (Traceability Matrix).
---

# Generování přehledu pokrytí User Stories automatizovanými testy

Tento skill slouží k opakovatelnému mapování a vyhodnocování pokrytí všech byznysových požadavků (User Stories) manuálními test casy a automatizovanými testy (Playwright + pytest).

---

## 1. Co skill dělá

1. **Automatická detekce a skenování:**
   * Prochází adresář `tests/` a zjišťuje všechny implementované automatizované testy (`def test_...`).
   * Analyzuje vazby na User Stories (např. `US-01`, `US03`, `US-11` atd.) v názvech a docstringách testů.
   * Prochází adresář `docs/testcases/` a počítá definované manuální test casy.
2. **Výpočet metrik pokrytí (KPIs):**
   * Celkový počet User Stories a procento pokrytí automatizovanými testy.
   * Počet automatizovaných testů připadajících na jednotlivé User Stories.
   * Identifikace nepokrytých nebo částečně pokrytých požadavků.
3. **Výstupy:**
   * **Interaktivní HTML report:** ukládá se do `reports/coverage_report.html` (respektuje pravidlo čistého kořene v `AGENTS.md`).
   * **Konzolový souhrn:** přehledná tabulka v terminálu.

---

## 2. Spuštění generování přehledu

Skript je plně opakovatelný – kdykoliv přidáte novou User Story, manuální test case nebo automatizovaný test, stačí skript znovu spustit:

```bash
python .agents/skills/coverage-report/scripts/generate_coverage_report.py
```

Volitelné parametry:
* `--output <cesta>`: Změna výstupního souboru (výchozí: `reports/coverage_report.html`).
* `--format [html|json|markdown]`: Formát výstupu.

---

## 3. Matice sledovatelnosti (Traceability)

Každá User Story je v reportu zařazena do jedné ze 3 kategorií:
* 🟢 **POKRYTO:** Pro User Story existuje alespoň jeden funkční automatizovaný test.
* 🟡 **POUZE MANUÁLNÍ TC:** Pro User Story existují manuální scénáře, ale chybí automatizovaný test.
* 🔴 **NEPOKRYTO:** User Story nemá žádný test.
