# Manuální Test Casy: US04 – Přihlášení studenta na termín kurzu

## 1. Zadání User Story
**Jako** student  
**chci** se přihlásit na volný termín kurzu,  
**abych** si zajistil místo.

### Akceptační kritéria:
* **AC1:** Přihlášení s platným telefonem a IČO.
* **AC2:** Odmítnutí neplatného formátu telefonu.
* **AC3:** Plně obsazený termín neumožňuje registraci.

---

## 2. Přehled Test Casů

| ID | Název testovacího případu | Pokrytá AC | Typ testu |
| :--- | :--- | :---: | :--- |
| **TC-01** | Úspěšné přihlášení na volný termín s platným telefonem a IČO | AC1 | Pozitivní |
| **TC-02** | Odmítnutí registrace s neplatným formátem telefonního čísla | AC2 | Negativní |
| **TC-03** | Validace prázdného pole telefonu při odeslání přihlášky | AC2 | Negativní |
| **TC-04** | Znemožnění registrace na plně obsazený termín kurzu | AC3 | Hraniční / Negativní |

---

## 3. Detailní scénáře Test Casů

### TC-01: Úspěšné přihlášení na volný termín s platným telefonem a IČO
* **Pokrytá kritéria:** AC1
* **Typ testu:** Pozitivní (Happy Path)
* **Předpoklady (Preconditions):**
  1. Uživatel je přihlášen v aplikaci jako student.
  2. V katalogu existuje kurz s alespoň jedním vypsaným termínem, který má volnou kapacitu (obsazenost < kapacita).
* **Kroky testu (Steps):**
  1. V navigačním menu klikni na „Kurzy“ (`/courses`).
  2. U vybraného kurzu klikni na tlačítko „Chci vidět více“ pro přechod na detail kurzu.
  3. V sekci termínů vyhledej volný termín a klikni na tlačítko „Nezávazná registrace“.
  4. Na zobrazeném formuláři vyplň do pole Telefon platné 9místné číslo (např. `777123456`).
  5. Do pole IČO vyplň platné osmimístné IČO (např. `27082440`).
  6. Klikni na tlačítko „Odeslat přihlášku“.
* **Očekávaný výsledek (Expected Result):**
  1. Formulář je úspěšně odeslán.
  2. Zobrazí se potvrzovací hláška o úspěšném přihlášení na termín kurzu (`Successfully enrolled`).
  3. Uživatel vidí termín zařazený ve svém přehledu na stránce „Moje kurzy“.

---

### TC-02: Odmítnutí registrace s neplatným formátem telefonního čísla
* **Pokrytá kritéria:** AC2
* **Typ testu:** Negativní (Validace formátu)
* **Předpoklady (Preconditions):**
  1. Uživatel je přihlášen jako student.
  2. Uživatel je otevřen na formuláři přihlášky na volný termín (`/courses/{id}/register`).
* **Kroky testu (Steps):**
  1. Do pole Telefon zadej neplatný textový nebo neúplný řetězec (např. `123abc` nebo `12345`).
  2. Do pole IČO zadej platné IČO (`27082440`).
  3. Klikni na tlačítko „Odeslat přihlášku“.
* **Očekávaný výsledek (Expected Result):**
  1. Formulář není odeslán a systém neprovede registraci uživatele na termín.
  2. Pod polem pro telefon se zobrazí jednoznačná validační chyba upozorňující na nesprávný formát čísla.
  3. Pole pro telefon je vizuálně zvýrazněno jako chybné.

---

### TC-03: Validace prázdného pole telefonu při odeslání přihlášky
* **Pokrytá kritéria:** AC2
* **Typ testu:** Negativní (Povinné pole)
* **Předpoklady (Preconditions):**
  1. Uživatel je přihlášen jako student.
  2. Uživatel se nachází na formuláři přihlášky na termín kurzu.
* **Kroky testu (Steps):**
  1. Pole Telefon ponech zcela prázdné.
  2. Do pole IČO zadej platné IČO (`27082440`).
  3. Klikni na tlačítko „Odeslat přihlášku“.
* **Očekávaný výsledek (Expected Result):**
  1. Žádost o registraci je zamítnuta.
  2. Zobrazí se validační hláška indikující, že telefon je povinný údaj.
  3. Uživatel zůstává na formuláři přihlášky.

---

### TC-04: Znemožnění registrace na plně obsazený termín kurzu
* **Pokrytá kritéria:** AC3
* **Typ testu:** Hraniční / Negativní (Kapacitní limit)
* **Předpoklady (Preconditions):**
  1. Uživatel je přihlášen jako student.
  2. U daného kurzu existuje termín, jehož kapacita je 100% naplněna (počet přihlášených = maximální kapacita).
* **Kroky testu (Steps):**
  1. Přejdi do katalogu kurzů (`/courses`) a otevři detail kurzu s plně obsazeným termínem.
  2. Vyhledej v tabulce termínů řádek s plně obsazenou kapacitou.
  3. Zkontroluj stav tlačítka pro registraci u tohoto termínu.
* **Očekávaný výsledek (Expected Result):**
  1. U plně obsazeného termínu se tlačítko „Nezávazná registrace“ vůbec nezobrazuje, nebo je v neaktivním (disabled) stavu s textem „Obsazeno“.
  2. Uživatel nemá možnost otevřít registrační formulář pro tento termín ani odeslat přihlášku.
