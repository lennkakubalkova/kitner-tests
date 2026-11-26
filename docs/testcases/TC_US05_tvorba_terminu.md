# Manuální Test Casy: US05 – Vypsání nového termínu (iterace) kurzu lektorem

## 1. Zadání User Story
**Jako** přihlášený lektor kurzu  
**chci** k existujícímu vzdělávacímu kurzu vypsat nový termín (datum od/do, den, čas a místo konání),  
**abych** studentům umožnil registraci na nový běh kurzu a současně byla zajištěna ochrana této akce před neoprávněnými uživateli.

### Akceptační kritéria:
* **AC1:** Lektor může otevřít formulář pro vypsání nového běhu kurzu a úspěšně jej vytvořit.
* **AC2:** Běžný přihlášený student ani anonymní návštěvník nemá přístup k tlačítku a formuláři pro tvorbu nového termínu.

---

## 2. Přehled Test Casů

| ID | Název testovacího případu | Pokrytá AC | Typ testu |
| :--- | :--- | :---: | :--- |
| **TC-01** | Lektor úspěšně vytvoří a vypíše nový termín kurzu | AC1 | Pozitivní (Happy Path - Lektor) |
| **TC-02** | Běžný student nemá přístup k vypsání nového termínu kurzu | AC2 | Bezpečnostní / Negativní (Role restriction) |

---

## 3. Detailní scénáře Test Casů

### TC-01: Lektor úspěšně vytvoří a vypíše nový termín kurzu
* **Pokrytá kritéria:** AC1
* **Typ testu:** Pozitivní (Happy Path - Lektor)
* **Předpoklady (Preconditions):**
  1. Uživatel je v aplikaci přihlášen s účtem lektora (`role_id = 2`).
  2. V aplikaci existuje vytvořený kurz.
* **Kroky testu (Steps):**
  1. V katalogu kurzů vyhledej existující kurz a klikni na tlačítko pro přidání nového termínu (ikona/tlačítko `add_iteration`).
  2. V zobrazeném modálním okně vyplň datum zahájení (`Datum od`), datum ukončení (`Datum do`).
  3. Zvol den v týdnu (např. `Pondělí`), čas konání (např. `17:00`) a místo konání (např. `Online / Učebna`).
  4. Klikni na tlačítko pro uložení termínu.
* **Očekávaný výsledek (Expected Result):**
  1. Nový termín je úspěšně vytvořen.
  2. Modální formulář se zavře.
  3. V sekci termínů daného kurzu je nový běh zobrazen s vyplněnými parametry.

---

### TC-02: Běžný student nemá přístup k vypsání nového termínu kurzu
* **Pokrytá kritéria:** AC2
* **Typ testu:** Bezpečnostní / Negativní (Role restriction)
* **Předpoklady (Preconditions):**
  1. Uživatel je přihlášen jako běžný zákazník/student (`role_id = 1`) nebo je odhlášen.
* **Kroky testu (Steps):**
  1. Otevři stránku s katalogem kurzů `/courses`.
  2. Zkontroluj ovládací prvky u karet kurzů.
* **Očekávaný výsledek (Expected Result):**
  1. Tlačítko pro přidání termínu kurzu (`add_iteration`) není pro studenta ani návštěvníka vůbec viditelné.
  2. Uživatel nemá možnost otevřít modální formulář pro vypsání běhu kurzu.

