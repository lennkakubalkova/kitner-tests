# Manuální Test Casy: US01 – Registrace nového uživatelského účtu

## 1. Zadání User Story
**Jako** nový uživatel portálu  
**chci** se zaregistrovat pomocí svého jména, platného e-mailu a hesla,  
**abych** si vytvořil zákaznický účet a mohl využívat všechny funkce portálu včetně zápisu na kurzy.

### Akceptační kritéria:
* **AC1:** Úspěšná registrace nového studenta s platnými údaji a vytvoření profilu.
* **AC2:** Validace povinných polí při odeslání prázdného registračního formuláře.
* **AC3:** Validace neshody hesla a potvrzení hesla.
* **AC4:** Odmítnutí registrace s již registrovanou e-mailovou adresou.

---

## 2. Přehled Test Casů

| ID | Název testovacího případu | Pokrytá AC | Typ testu |
| :--- | :--- | :---: | :--- |
| **TC-01** | Úspěšná registrace nového studenta s platnými údaji | AC1 | Pozitivní (Happy Path) |
| **TC-02** | Validace odeslání prázdného registračního formuláře | AC2 | Negativní (Validace) |
| **TC-03** | Odmítnutí registrace při neshodě zadaných hesel | AC3 | Negativní (Validace hesla) |
| **TC-04** | Odmítnutí registrace s již registrovanou e-mailovou adresou | AC4 | Negativní (Duplicita) |

---

## 3. Detailní scénáře Test Casů

### TC-01: Úspěšná registrace nového studenta s platnými údaji
* **Pokrytá kritéria:** AC1
* **Typ testu:** Pozitivní (Happy Path)
* **Předpoklady (Preconditions):**
  1. Uživatel není přihlášen.
  2. Je k dispozici unikátní dosud neregistrovaná e-mailová adresa.
* **Kroky testu (Steps):**
  1. Otevři registrační stránku `/register`.
  2. Do pole Jméno vyplň platné jméno uživatele (např. `Jan Testovací`).
  3. Do pole E-mail vyplň unikátní platnou e-mailovou adresu.
  4. Do polí Heslo a Potvrzení hesla vyplň shodné heslo o délce alespoň 8 znaků.
  5. Klikni na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek (Expected Result):**
  1. Registrační formulář je úspěšně odeslán.
  2. Uživatel je automaticky přihlášen a přesměrován do aplikace.
  3. V horní navigaci je viditelné tlačítko pro odhlášení.

---

### TC-02: Validace odeslání prázdného registračního formuláře
* **Pokrytá kritéria:** AC2
* **Typ testu:** Negativní (Validace)
* **Předpoklady (Preconditions):**
  1. Uživatel je otevřen na registrační stránce `/register`.
* **Kroky testu (Steps):**
  1. Ponech všechna formulářová pole prázdná.
  2. Klikni na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek (Expected Result):**
  1. Registrace neproběhne a uživatel zůstává na registrační stránce.
  2. U formulářových polí se zobrazí validační chybové hlášky upozorňující na povinnost vyplnění údajů.

---

### TC-03: Odmítnutí registrace při neshodě zadaných hesel
* **Pokrytá kritéria:** AC3
* **Typ testu:** Negativní (Validace hesla)
* **Předpoklady (Preconditions):**
  1. Uživatel je otevřen na registrační stránce `/register`.
* **Kroky testu (Steps):**
  1. Vyplň platné jméno a unikátní e-mailovou adresu.
  2. Do pole Heslo zadej platné heslo (např. `Heslo1234`).
  3. Do pole Potvrzení hesla zadej odlišné heslo (např. `JineHeslo999`).
  4. Klikni na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek (Expected Result):**
  1. Registrace není dokončena.
  2. U pole potvrzení hesla se zobrazí chybová hláška informující o neshodě zadaných hesel.

---

### TC-04: Odmítnutí registrace s již registrovanou e-mailovou adresou
* **Pokrytá kritéria:** AC4
* **Typ testu:** Negativní (Duplicita)
* **Předpoklady (Preconditions):**
  1. V databázi existuje dříve zaregistrovaný uživatel s daným e-mailem.
* **Kroky testu (Steps):**
  1. Otevři registrační stránku `/register`.
  2. Vyplň jméno a do pole E-mail zadej existující e-mail registrovaného uživatele.
  3. Vyplň platná shodná hesla.
  4. Klikni na tlačítko „Zaregistrovat se“.
* **Očekávaný výsledek (Expected Result):**
  1. Systém odmítne registraci duplicitního e-mailu.
  2. Zobrazí se validační chyba informující, že daný e-mail je již v systému zaregistrován.

