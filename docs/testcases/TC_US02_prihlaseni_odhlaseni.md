# Manuální Test Casy: US02 – Přihlášení a odhlášení uživatele

## 1. Zadání User Story
**Jako** registrovaný uživatel nebo lektor  
**chci** se přihlásit do aplikace svými přihlašovacími údaji a kdykoliv se bezpečně odhlásit,  
**abych** získal přístup k funkcím podle své role a po skončení práce ochránil své sezení.

### Akceptační kritéria:
* **AC1:** Úspěšné přihlášení s platnými údaji a zobrazení ovládacích prvků přihlášeného stavu.
* **AC2:** Odmítnutí přihlášení při zadání neplatného hesla nebo neexistujícího účtu.
* **AC3:** Úspěšné a bezpečné odhlášení ze systému s ukončením sezení.

---

## 2. Přehled Test Casů

| ID | Název testovacího případu | Pokrytá AC | Typ testu |
| :--- | :--- | :---: | :--- |
| **TC-01** | Úspěšné přihlášení registrovaného uživatele do aplikace | AC1 | Pozitivní (Happy Path) |
| **TC-02** | Odmítnutí přihlášení s neplatným heslem | AC2 | Negativní (Autentizace) |
| **TC-03** | Bezpečné odhlášení přihlášeného uživatele ze systému | AC3 | Pozitivní (Session security) |

---

## 3. Detailní scénáře Test Casů

### TC-01: Úspěšné přihlášení registrovaného uživatele do aplikace
* **Pokrytá kritéria:** AC1
* **Typ testu:** Pozitivní (Happy Path)
* **Předpoklady (Preconditions):**
  1. V systému existuje vytvořený uživatelský účet s platným heslem.
  2. Uživatel je ve stavu nepřihlášen.
* **Kroky testu (Steps):**
  1. Otevři přihlašovací stránku `/login`.
  2. Do pole E-mail zadej platnou e-mailovou adresu registrovaného účtu.
  3. Do pole Heslo zadej správné heslo k účtu.
  4. Klikni na tlačítko „Přihlásit se“.
* **Očekávaný výsledek (Expected Result):**
  1. Uživatel je úspěšně přihlášen a přesměrován do aplikace.
  2. V horní navigační liště se zobrazí tlačítko „Odhlásit se“.
  3. Odkaz na přihlášení již není v navigaci viditelný.

---

### TC-02: Odmítnutí přihlášení s neplatným heslem
* **Pokrytá kritéria:** AC2
* **Typ testu:** Negativní (Autentizace)
* **Předpoklady (Preconditions):**
  1. V systému existuje vytvořený uživatelský účet.
* **Kroky testu (Steps):**
  1. Otevři přihlašovací stránku `/login`.
  2. Zadej platný e-mail uživatele.
  3. Do pole Heslo zadej chybné/neplatné heslo (např. `SpatneHeslo123`).
  4. Klikni na tlačítko „Přihlásit se“.
* **Očekávaný výsledek (Expected Result):**
  1. Uživatel není přihlášen a zůstává na přihlašovací stránce.
  2. Zobrazí se chybová validační hláška upozorňující na nesprávné přihlašovací údaje.

---

### TC-03: Bezpečné odhlášení přihlášeného uživatele ze systému
* **Pokrytá kritéria:** AC3
* **Typ testu:** Pozitivní (Session security)
* **Předpoklady (Preconditions):**
  1. Uživatel je přihlášen v aplikaci.
* **Kroky testu (Steps):**
  1. V horní navigaci vyhledej a klikni na tlačítko „Odhlásit se“.
* **Očekávaný výsledek (Expected Result):**
  1. Uživatelská relace (session) je ukončena.
  2. V navigaci se opět zobrazí odkaz „Přihlásit se“.
  3. Privátní prvky a tlačítko „Odhlásit se“ již nejsou viditelné.

