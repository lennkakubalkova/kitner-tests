---
name: kitner-locators
description: Použij vždy, když vytváříš nebo upravuješ automatizované testy, píšeš Page Objecty nebo hledáš a definuješ lokátory prvků pro portál testovani.kitner.cz.
---

# Pravidla pro lokátory v projektu Kitner

## 1. Povolené lokátory
* Používej **výhradně** atributy `data-test` a `data-testid` (např. `page.locator('[data-test="submit_button"]')`).
* Je zakázáno používat křehké selektory: absolutní XPath, hluboce zanořené CSS cesty (`div > div:nth-child(2)`) nebo selektory závislé na barvách a proměnlivém textu.
* Všechny lokátory musí být zapouzdřeny v **Page Objectech** (`pages/`), nikdy se nepíší přímo do testovacích funkcí v `tests/`.
* Kompletní přehled existujících selektorů je v souboru `lokatory.md`.

## 2. Co dělat, když prvek nemá data-test atribut (STOP pravidlo)
* **Nikdy neimprovizuj** a nepoužívej náhradní nestabilní selektory.
* Okamžitě **zastav práci** na daném kroku a **nahlás uživateli**, že prvek postrádá `data-test` atribut.
* Do hlášení uveď:
  1. O jakou stránku a prvek se jedná (název komponenty).
  2. Navrhovaný název atributu (např. `Doplňte do HTML atribut: data-test="order_submit_btn"`).
