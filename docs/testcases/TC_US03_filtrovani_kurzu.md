# Manuální Test Casy: US03 – Vyhledávání a filtrování kurzů v katalogu

## 1. Zadání User Story
**Jako** návštěvník nebo student  
**chci** vyhledávat kurzy podle klíčového slova a filtrovat je podle volné kapacity,  
**abych** rychle našel odpovídající kurz s volnými místy bez nutnosti procházet celý katalog.

### Akceptační kritéria:
* **AC1:** Vyhledávání kurzů podle zadaného textového řetězce v názvu kurzu.
* **AC2:** Filtrování kurzů podle minimální požadované kapacity volných míst.
* **AC3:** Zobrazení prázdného výsledku a informace při nenalezení žádného kurzu.

---

## 2. Přehled Test Casů

| ID | Název testovacího případu | Pokrytá AC | Typ testu |
| :--- | :--- | :---: | :--- |
| **TC-01** | Úspěšné vyhledání kurzu podle klíčového slova v katalogu | AC1 | Pozitivní (Vyhledávání) |
| **TC-02** | Filtrování nabídky kurzů podle minimální volné kapacity | AC2 | Pozitivní (Filtrace kapacity) |
| **TC-03** | Vyhledání neexistujícího výrazu a zobrazení prázdného výsledku | AC3 | Hraniční / Negativní (Prázdný stav) |

---

## 3. Detailní scénáře Test Casů

### TC-01: Úspěšné vyhledání kurzu podle klíčového slova v katalogu
* **Pokrytá kritéria:** AC1
* **Typ testu:** Pozitivní (Vyhledávání)
* **Předpoklady (Preconditions):**
  1. Uživatel otevře stránku s katalogem kurzů `/courses`.
  2. V nabídce existují kurzy obsahující známé klíčové slovo (např. `Automatizované`).
* **Kroky testu (Steps):**
  1. Do vyhledávacího pole pro název kurzu zadej klíčové slovo (např. `Automatizované`).
* **Očekávaný výsledek (Expected Result):**
  1. Seznam kurzů se dynamicky vyfiltruje.
  2. Zobrazují se pouze kurzy, jejichž název obsahuje hledané klíčové slovo.

---

### TC-02: Filtrování nabídky kurzů podle minimální volné kapacity
* **Pokrytá kritéria:** AC2
* **Typ testu:** Pozitivní (Filtrace kapacity)
* **Předpoklady (Preconditions):**
  1. Uživatel je na stránce katalogu kurzů `/courses`.
* **Kroky testu (Steps):**
  1. Do pole filtru kapacity zadej minimální počet volných míst (např. `5`).
* **Očekávaný výsledek (Expected Result):**
  1. Zobrazují se výhradně kurzy splňující podmínku zadané minimální kapacity.
  2. Kurzy s nižší než požadovanou kapacitou jsou ze zobrazení skryty.

---

### TC-03: Vyhledání neexistujícího výrazu a zobrazení prázdného výsledku
* **Pokrytá kritéria:** AC3
* **Typ testu:** Hraniční / Negativní (Prázdný stav)
* **Předpoklady (Preconditions):**
  1. Uživatel je otevřen na katalogu kurzů `/courses`.
* **Kroky testu (Steps):**
  1. Do vyhledávacího pole zadej nesmyslný nebo neexistující řetězec (např. `NeexistujiciKurz123XYZ`).
* **Očekávaný výsledek (Expected Result):**
  1. V katalogu se nezobrazí žádná karta kurzu.
  2. Stránka korektně indikuje, že žádné kurzy neodpovídají zadanému filtru.

