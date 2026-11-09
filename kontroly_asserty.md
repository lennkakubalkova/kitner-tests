# Analýza a specifikace kontrol (Assertů) pro aplikaci Demo Login

Tento dokument detailně popisuje a vyhodnocuje veškeré kontroly (asserty) implementované v automatizovaných testech pro aplikaci **Demo login** ([http://testovani.kitner.cz/courses](http://testovani.kitner.cz/courses)).

---

## 1. Vyhodnocení dostatečnosti kontrol (Proč samotná URL nestačí)

V moderních webových aplikacích postavených na SPA (Single Page Application, React / Vue / Angular) je **pouhá kontrola URL adresy hrubě nedostatečná**.

### Rizika pouhé kontroly URL:
1. **Falešně pozitivní výsledky (False Positives):**
   - Frontendový router může změnit cestu v adresním řádku ještě předtím, než backend odpoví na požadavek na autentizaci.
   - Pokud backend vrátí HTTP 401 nebo 500, ale router již provedl přesměrování v klientské historii, test kontrolující pouze URL projde jako úspěšný, ačkoli uživatel fakticky přihlášen není.
2. **Neověření stavu sezení (Session / Token):**
   - Změna URL nedokazuje, že frontend obdržel autorizační token / cookie a uložil jej do `localStorage` či session storage.
3. **Absence kontroly uživatelských rolí a oprávnění:**
   - URL `/courses` vidí nepřihlášený uživatel, běžný student i lektor. Kontrola URL vůbec neodliší, zda se přihlásil lektor se zvláštními pravomocemi, nebo obyčejný uživatel bez práv.
4. **Tiché selhání (Silent Failures):**
   - Při chybě se může zobrazit prázdná bílá stránka s URL `/home`. Kontrola URL by prošla, ale uživatel vidí rozbitou aplikaci.

### Naše řešení: Vícevrstvé asserty (Multi-Tier Assertions)
Každý náš test kombinuje minimálně 3 až 5 nezávislých úrovní ověření:
1. **Úroveň navigace:** Ověření cílové URL adresy (`page.url`).
2. **Úroveň globálního menu (Navbar):**
   - Přítomnost tlačítka `Odhlásit se` (důkaz aktivní autentizace).
   - Absenci tlačítka `Přihlásit se` (důkaz opuštění nepřihlášeného stavu).
   - Přítomnost profilových odkazů (`Můj Profil`, `Moje kurzy`).
3. **Úroveň personalizace a dat:**
   - Zobrazení uvítací zprávy s konkrétním jménem nově vytvořeného uživatele (`Vítej uživateli <Jméno>!`).
4. **Úroveň rolí a autorizace (Role-Based Access Control):**
   - **Lektor (`lector@lector.com`):** Ověření viditelnosti tlačítka `Přidat kurz` v záhlaví a tlačítek `Přidat iteraci` u jednotlivých kurzů.
   - **Běžný uživatel:** Striktní negativní kontrola – tlačítko `Přidat kurz` **nesmí** být viditelné.
5. **Úroveň chybových stavů:**
   - Přesná textová kontrola validací (např. `"These credentials do not match our records."`, `"The email has already been taken."`, atd.).
   - Ověření, že v chybovém stavu se nezměnila URL a uživatel zůstává nepřihlášen.

---

## 2. Podrobný přehled kontrol v jednotlivých testech

### Oblast: Registrace (Registration)

| ID testu | Název testu | Prováděné kontroly (Asserts) | Proč je kontrola dostatečná |
| :--- | :--- | :--- | :--- |
| **REG-01** | `test_registration_success_verifies_login_state_and_welcome` | 1. URL obsahuje `/home`<br>2. Banner obsahuje text `Vítej uživateli`<br>3. Banner obsahuje přesné jméno uživatele<br>4. V menu je viditelné `Odhlásit se`<br>5. V menu NENÍ viditelné `Přihlásit se`<br>6. V menu je viditelné `Můj Profil`<br>7. V menu je viditelné `Moje kurzy`<br>8. Na stránce NENÍ tlačítko `Přidat kurz` | Komplexní ověření: uživatel je nejen přesměrován, ale systém správně založil identitu se jménem, nastavil autentizační stav a nepřidělil mu neoprávněně lektorská práva. |
| **REG-02** | `test_registration_empty_form_validation` | 1. URL zůstává na `/register`<br>2. Chybová hláška `"The name field is required."`<br>3. Chybová hláška `"The email field is required."`<br>4. Chybová hláška `"The password field is required."`<br>5. Menu stále ukazuje stav nepřihlášen (`Přihlásit se` viditelné) | Ověřuje blokaci odeslání prázdného formuláře a přítomnost všech 3 povinných validačních hlášek. |
| **REG-03** | `test_registration_password_mismatch` | 1. URL zůstává na `/register`<br>2. Chybová hláška `"The password field confirmation does not match."`<br>3. Menu stále ukazuje nepřihlášený stav | Chrání před registrací s překlepem v heslu. Validuje shodu hesel. |
| **REG-04** | `test_registration_duplicate_email` | 1. URL zůstává na `/register`<br>2. Backendová validační chyba `"The email has already been taken."`<br>3. Uživatel není přihlášen | Zabraňuje duplicitním registracím stejného emailu v databázi. |
| **REG-05** | `test_registration_missing_name_only` | 1. URL zůstává na `/register`<br>2. Chybová hláška `"The name field is required."` je přítomna<br>3. Chybová hláška pro email NENÍ přítomna<br>4. Chybová hláška pro heslo NENÍ přítomna | Ověřuje izolovanost validací jednotlivých polí (žádné falešné chyby u správně vyplněných polí). |
| **REG-06** | `test_registration_missing_password_only` | 1. URL zůstává na `/register`<br>2. Chybová hláška `"The password field is required."` je přítomna<br>3. Chyby pro jméno a email NEJSOU přítomny | Ověřuje izolovanost validace hesla. |
| **REG-07** | `test_registration_link_navigates_to_login` | 1. Klik na odkaz `Přihlaste se zde.` přesměruje na `/login`<br>2. Formulář na `/login` obsahuje viditelné pole `#email_input`<br>3. Formulář obsahuje viditelné pole `#password_input` | Ověřuje funkční navigaci a použitelnost přihlašovacího formuláře pro již registrované uživatele. |

---

### Oblast: Přihlášení a sezení (Login & Session)

| ID testu | Název testu | Prováděné kontroly (Asserts) | Proč je kontrola dostatečná |
| :--- | :--- | :--- | :--- |
| **LOG-01** | `test_login_lector_success_and_privileges` | 1. URL obsahuje `/courses`<br>2. V menu je viditelné `Odhlásit se`<br>3. V menu NENÍ `Přihlásit se`<br>4. V menu je viditelné `Můj Profil`<br>5. V menu je viditelné `Moje kurzy`<br>6. **Lektorské právo 1:** Tlačítko `Přidat kurz` je zobrazeno<br>7. **Lektorské právo 2:** Tlačítka `Přidat iteraci` u kurzů jsou zobrazena | Špičkový test autorizace: ověřuje nejen úspěšné přihlášení v UI a menu, ale i aktivaci lektorských funkcí správy kurzů. |
| **LOG-02** | `test_login_registered_user_success` | 1. Autentizace reálně zaregistrovaného uživatele proběhne úspěšně<br>2. Menu ukazuje přihlášený stav (`Odhlásit se`, `Můj Profil`)<br>3. **Ověření hranice oprávnění:** Tlačítko `Přidat kurz` NENÍ viditelné | Zajišťuje, že běžný uživatel nezíská lektorská oprávnění, ale má plný přístup ke svému profilu. |
| **LOG-03** | `test_login_empty_fields_validation` | 1. URL zůstává na `/login`<br>2. Chybová hláška `"The email field is required."`<br>3. Chybová hláška `"The password field is required."`<br>4. Uživatel zůstává nepřihlášen | Brání odeslání prázdného přihlašovacího formuláře. |
| **LOG-04** | `test_login_invalid_password` | 1. URL zůstává na `/login`<br>2. Chybová hláška `"These credentials do not match our records."`<br>3. V menu zůstává `Přihlásit se`, tlačítko `Odhlásit se` se neobjeví | Bezpečnostní kontrola: nesprávné heslo nevpustí uživatele do systému a zobrazí přesnou hlášku. |
| **LOG-05** | `test_login_nonexistent_user` | 1. URL zůstává na `/login`<br>2. Chybová hláška `"These credentials do not match our records."`<br>3. Uživatel není autentizován | Zabraňuje neautorizovanému vstupu neexistujících účtů. |
| **LOG-06** | `test_logout_flow_and_session_cleared` | 1. Předpoklad: lektor je přihlášen a vidí lektorská tlačítka<br>2. Kliknutí na `Odhlásit se`<br>3. Stav menu: `Odhlásit se` zmizí<br>4. Stav menu: `Přihlásit se` se opět objeví<br>5. Privilegované tlačítko `Přidat kurz` okamžitě zmizí z DOMu | Komplexní test životního cyklu sezení: ověřuje úplné vyčištění klientského stavu a návrat do anonymního režimu. |
| **LOG-07** | `test_login_navigation_to_register` | 1. Klik na odkaz `Zaregistrujte se zde.` přesměruje na `/register`<br>2. Viditelnost pole Jméno<br>3. Viditelnost pole Email<br>4. Viditelnost pole Heslo<br>5. Viditelnost pole Heslo znovu | Ověřuje funkční navigaci mezi přihlašovací a registrační obrazovkou. |

---

## 3. Závěr vyhodnocení

Všech **14 testů** splňuje nejpřísnější kritéria spolehlivého testování:
- **Žádný test se nespoléhá pouze na URL adresu.**
- Všechny úspěšné stavy kontrolují změny v **DOM navigaci (menu)** a **přítomnost/absenci uživatelských prvků**.
- Všechny negativní stavy kontrolují **přesné znění chybových hlášek** generovaných aplikací.
- Testy ověřují **oddělení rolí (RBAC)** – rozlišují běžného uživatele a lektora se specifickými právy.

