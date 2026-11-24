# Manuální Test Casy: US13 – Zobrazení přihlášených kurzů (Moje kurzy)

## 1. Zadání User Story
**Jako** přihlášený student  
**chci** mít přehled svých přihlášených kurzů na stránce „Moje kurzy“,  
**abych** viděl termíny svých vzdělávacích akcí a stav své registrace.

### Akceptační kritéria:
* **AC1:** Zabezpečení přístupu – nepřihlášený návštěvník nevidí odkaz „Moje kurzy“ v horní navigaci.
* **AC2:** Dostupnost a zobrazení přehledu pro přihlášeného studenta přes navigaci (`/my-courses`).
* **AC3:** Zobrazení přihlášeného kurzu po provedení nezávazné registrace na vypsaný termín.

---

## 2. Přehled Test Casů

| ID | Název testovacího případu | Pokrytá AC | Typ testu |
| :--- | :--- | :---: | :--- |
| **TC-01** | Odkaz Moje kurzy není dostupný pro nepřihlášeného návštěvníka | AC1 | Bezpečnostní / Negativní |
| **TC-02** | Přihlášený student může otevřít sekci Moje kurzy z hlavního menu | AC2 | Pozitivní |
| **TC-03** | Ověření zobrazení zapsaného termínu v přehledu Moje kurzy po registraci | AC3 | Pozitivní (End-to-End) |

---

## 3. Detailní scénáře Test Casů

### TC-01: Odkaz Moje kurzy není dostupný pro nepřihlášeného návštěvníka
* **Pokrytá kritéria:** AC1
* **Typ testu:** Bezpečnostní / Negativní (Guest restriction)
* **Předpoklady (Preconditions):**
  1. Uživatel není přihlášen (stav anonymní návštěvník).
* **Kroky testu (Steps):**
  1. Otevři hlavní stránku aplikace (`/courses`).
  2. Zkontroluj položky horního navigačního menu.
* **Očekávaný výsledek (Expected Result):**
  1. V navigační liště se odkaz „Moje kurzy“ vůbec nezobrazuje.
  2. Jsou viditelné pouze veřejné položky: „Kurzy“ a „Přihlásit se“.

---

### TC-02: Přihlášený student může otevřít sekci Moje kurzy z hlavního menu
* **Pokrytá kritéria:** AC2
* **Typ testu:** Pozitivní (Navigace přihlášeného uživatele)
* **Předpoklady (Preconditions):**
  1. Uživatel má existující zákaznický účet a je přihlášen v aplikaci.
* **Kroky testu (Steps):**
  1. Zkontroluj položky horního navigačního menu po přihlášení.
  2. Klikni na odkaz „Moje kurzy“ v navigaci.
* **Očekávaný výsledek (Expected Result):**
  1. Odkaz „Moje kurzy“ je v menu viditelný.
  2. Prohlížeč přesměruje uživatele na URL `/my-courses`.
  3. Kontejner stránky přehledu mých kurzů se úspěšně načte bez chyb.

---

### TC-03: Ověření zobrazení zapsaného termínu v přehledu Moje kurzy po registraci
* **Pokrytá kritéria:** AC3
* **Typ testu:** Pozitivní (End-to-End ověření zapsaného kurzu)
* **Předpoklady (Preconditions):**
  1. Uživatel je přihlášen jako student.
  2. V katalogu kurzů existuje volný termín kurzu.
* **Kroky testu (Steps):**
  1. Přejdi do katalogu kurzů a otevři detail kurzu.
  2. U volného termínu klikni na „Nezávazná registrace“.
  3. Vyplň formulář přihlášky (telefon a IČO) a odešli jej.
  4. Po potvrzení registrace přejdi v menu do sekce „Moje kurzy“.
* **Očekávaný výsledek (Expected Result):**
  1. Stránka `/my-courses` zobrazuje kontejner se zapsaným kurzem.
  2. V přehledu je viditelný odpovídající zapsaný kurz.
