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

### Naše řešení: Vícevrstvé asserty s využitím `data-test` / `data-testid`
Každý náš test kombinuje minimálně 3 až 5 nezávislých úrovní ověření:
1. **Úroveň navigace:** Ověření cílové URL adresy (`page.url`).
2. **Úroveň globálního menu (Navbar):**
   - Přítomnost tlačítka `Odhlásit se` s lokátorem `[data-test="logout_button"]` (důkaz aktivní autentizace).
   - Absenci tlačítka `Přihlásit se` s lokátorem `[data-test="login_link"]` (důkaz opuštění nepřihlášeného stavu).
   - Přítomnost profilových odkazů (`[data-test="courses_profile"]`, `[data-test="home_link"]`).
3. **Úroveň personalizace a dat:**
   - Zobrazení uvítací zprávy s konkrétním jménem nově vytvořeného uživatele (`Vítej uživateli <Jméno>!`).
4. **Úroveň rolí a autorizace (Role-Based Access Control):**
   - **Lektor (`lector@lector.com`):** Ověření viditelnosti tlačítka `Přidat kurz` a tlačítek `Přidat iteraci` u jednotlivých kurzů. Možnost otevřít modální okno `[data-test="course_form_container"]` a reálně založit nový kurz.
   - **Běžný uživatel / Anonym:** Striktní negativní kontrola – tlačítko `Přidat kurz` **nesmí** být viditelné.
5. **Úroveň chybových stavů:**
   - Přesná textová kontrola validací (např. `"These credentials do not match our records."`, `"The email has already been taken."`, atd.).
   - Ověření, že v chybovém stavu se nezměnila URL a formulář nebyl odeslán.

---

## 2. Podrobný přehled kontrol v jednotlivých testech

### Oblast 1: Přehled a správa kurzů (Courses & Catalog)

| ID testu | Název testu | Prováděné kontroly (Asserts) | Proč je kontrola dostatečná |
| :--- | :--- | :--- | :--- |
| **CRS-01** | `test_courses_list_visible_for_guest` | 1. Nadpis `[data-test="courses_title"]` je viditelný<br>2. Karty kurzů `[data-test^="course_"]` existují v počtu > 0<br>3. Zobrazena pole `[data-test="course_name"]`, `[data-test="course_price"]`, `[data-test="course_capacity"]`<br>4. Tlačítko `Přidat kurz` NENÍ zobrazeno | Ověřuje plnou dostupnost katalogu pro veřejnost a správné oddělení práv (anonym nemůže spravovat kurzy). |
| **CRS-02** | `test_regular_user_cannot_access_course_management` | 1. Uživatel je přihlášen<br>2. Tlačítko `Přidat kurz` NENÍ zobrazeno<br>3. Tlačítka `Přidat iteraci` NEJSOU zobrazena | Bezpečnostní autorizační test: student nesmí mít přístup k lektorským nástrojům. |
| **CRS-03** | `test_lector_can_open_create_course_modal` | 1. Tlačítko `Přidat kurz` je pro lektora viditelné<br>2. Modál `[data-test="course_form_container"]` se otevře<br>3. Pole `course_name_input`, `course_description_input`, `course_capacity_input`, `course_price_input` a tlačítko `Vytvořit kurz` jsou přítomna | Ověřuje kompletní formulářovou výbavu lektora pro tvorbu nových vzdělávacích akcí. |
| **CRS-04** | `test_lector_can_create_new_course` | 1. Úspěšné odeslání nového kurzu s unikátním názvem<br>2. Nově vytvořený kurz se reálně nachází v seznamu kurzů | End-to-end ověření tvorby kurzu od formuláře přes backend až po zobrazení v UI (US-14). |
| **CRS-05** | `test_course_detail_navigation_and_info` | 1. Klik na 'Chci vidět více'<br>2. Přesměrování na /courses/{id}<br>3. Zobrazení názvu, popisu, ceny a sekce vypsaných termínů | Komplexní zobrazení detailu kurzu a termínů (US-10). |
| **CRS-06** | `test_course_detail_full_capacity_disables_registration` | 1. Otevření detailu kurzu<br>2. U termínů s plnou kapacitou se nenabízí tlačítko zápisu pro nepřihlášeného hosta | Zamezení zápisu a indikace plné kapacity (US-11). |
| **CRS-07** | `test_lector_can_open_add_iteration_modal` | 1. Klik lektora na 'Přidat iteraci'<br>2. Zobrazení modálu `create_course_iteration_container`<br>3. Přítomnost polí pro datum od, datum do, den v týdnu, čas konání a místo výuky | Kompletní formulářová výbava pro vypsání nového běhu kurzu lektorem (US-15). |
| **CRS-08** | `test_lector_sees_participants_button_on_course_detail` | 1. Přihlášení lektora a otevření detailu kurzu<br>2. Přítomnost tlačítek 'Přihlášení' u termínů | Zpřístupnění seznamu zapsaných účastníků výhradně lektorovi (US-16). |

---

### Oblast 2: Registrace (Registration)

| ID testu | Název testu | Prováděné kontroly (Asserts) | Proč je kontrola dostatečná |
| :--- | :--- | :--- | :--- |
| **REG-01** | `test_registration_success_verifies_login_state_and_welcome` | 1. URL obsahuje `/home`<br>2. Banner obsahuje text `Vítej uživateli`<br>3. Banner obsahuje přesné jméno uživatele<br>4. V menu je viditelné `[data-test="logout_button"]`<br>5. V menu NENÍ viditelné `[data-test="login_link"]`<br>6. V menu je viditelné `[data-test="courses_profile"]`<br>7. V menu je viditelné `Moje kurzy`<br>8. Na stránce NENÍ tlačítko `Přidat kurz` | Komplexní ověření: uživatel je nejen přesměrován, ale systém správně založil identitu se jménem, nastavil autentizační stav a nepřidělil mu neoprávněně lektorská práva. |
| **REG-02** | `test_registration_empty_form_validation` | 1. URL zůstává na `/register`<br>2. Chybová hláška `"The name field is required."`<br>3. Chybová hláška `"The email field is required."`<br>4. Chybová hláška `"The password field is required."`<br>5. Menu stále ukazuje stav nepřihlášen (`[data-test="login_link"]` viditelné) | Ověřuje blokaci odeslání prázdného formuláře a přítomnost všech 3 povinných validačních hlášek. |
| **REG-03** | `test_registration_password_mismatch` | 1. URL zůstává na `/register`<br>2. Chybová hláška `"The password field confirmation does not match."`<br>3. Menu stále ukazuje nepřihlášený stav | Chrání před registrací s překlepem v heslu. Validuje shodu hesel. |
| **REG-04** | `test_registration_duplicate_email` | 1. URL zůstává na `/register`<br>2. Backendová validační chyba `"The email has already been taken."`<br>3. Uživatel není přihlášen | Zabraňuje duplicitním registracím stejného emailu v databázi. |
| **REG-05** | `test_registration_missing_name_only` | 1. URL zůstává na `/register`<br>2. Chybová hláška `"The name field is required."` je přítomna<br>3. Chybová hláška pro email NENÍ přítomna<br>4. Chybová hláška pro heslo NENÍ přítomna | Ověřuje izolovanost validací jednotlivých polí (žádné falešné chyby u správně vyplněných polí). |
| **REG-06** | `test_registration_missing_password_only` | 1. URL zůstává na `/register`<br>2. Chybová hláška `"The password field is required."` je přítomna<br>3. Chyby pro jméno a email NEJSOU přítomny | Ověřuje izolovanost validace hesla. |
| **REG-07** | `test_registration_link_navigates_to_login` | 1. Klik na odkaz `p[data-test="login_p"] a[data-test="login_link"]` přesměruje na `/login`<br>2. Formulář na `/login` obsahuje viditelné pole `input[data-test="email_input"]`<br>3. Formulář obsahuje viditelné pole `input[data-test="password_input"]` | Ověřuje funkční navigaci a použitelnost přihlašovacího formuláře pro již registrované uživatele. |
| **REG-08** | `test_registration_duplicate_email_case_insensitive` | 1. Pokus o registraci existujícího účtu s mezerami a velkými písmeny (`  LECTOR@LECTOR.COM  `)<br>2. Zobrazení chybové hlášky `"The email has already been taken."`<br>3. Uživatel není vpuštěn | Splňuje kritérium US-02: normalizace emailu a necitlivost na velikost písmen při ověřování unikátnosti. |

---

### Oblast 3: Přihlášení a sezení (Login & Session)

| ID testu | Název testu | Prováděné kontroly (Asserts) | Proč je kontrola dostatečná |
| :--- | :--- | :--- | :--- |
| **LOG-01** | `test_login_lector_success_and_privileges` | 1. URL obsahuje `/courses`<br>2. V menu je viditelné `[data-test="logout_button"]`<br>3. V menu NENÍ `[data-test="login_link"]`<br>4. V menu je viditelné `[data-test="courses_profile"]`<br>5. V menu je viditelné `Moje kurzy`<br>6. **Lektorské právo 1:** Tlačítko `Přidat kurz` je zobrazeno<br>7. **Lektorské právo 2:** Tlačítka `Přidat iteraci` u kurzů jsou zobrazena | Špičkový test autorizace: ověřuje nejen úspěšné přihlášení v UI a menu, ale i aktivaci lektorských funkcí správy kurzů. |
| **LOG-02** | `test_login_registered_user_success` | 1. Autentizace reálně zaregistrovaného uživatele proběhne úspěšně<br>2. Menu ukazuje přihlášený stav (`[data-test="logout_button"]`, `[data-test="courses_profile"]`)<br>3. **Ověření hranice oprávnění:** Tlačítko `Přidat kurz` NENÍ viditelné | Zajišťuje, že běžný uživatel nezíská lektorská oprávnění, ale má plný přístup ke svému profilu. |
| **LOG-03** | `test_login_empty_fields_validation` | 1. URL zůstává na `/login`<br>2. Chybová hláška `"The email field is required."`<br>3. Chybová hláška `"The password field is required."`<br>4. Uživatel zůstává nepřihlášen | Brání odeslání prázdného přihlašovacího formuláře. |
| **LOG-04** | `test_login_invalid_password` | 1. URL zůstává na `/login`<br>2. Chybová hláška `"These credentials do not match our records."`<br>3. V menu zůstává `[data-test="login_link"]`, tlačítko `[data-test="logout_button"]` se neobjeví | Bezpečnostní kontrola: nesprávné heslo nevpustí uživatele do systému a zobrazí přesnou hlášku. |
| **LOG-05** | `test_login_nonexistent_user` | 1. URL zůstává na `/login`<br>2. Chybová hláška `"These credentials do not match our records."`<br>3. Uživatel není autentizován | Zabraňuje neautorizovanému vstupu neexistujících účtů. |
| **LOG-06** | `test_logout_flow_and_session_cleared` | 1. Předpoklad: lektor je přihlášen a vidí lektorská tlačítka<br>2. Kliknutí na `[data-test="logout_button"]`<br>3. Stav menu: `[data-test="logout_button"]` zmizí<br>4. Stav menu: `[data-test="login_link"]` se opět objeví<br>5. Privilegované tlačítko `Přidat kurz` okamžitě zmizí z DOMu | Komplexní test životního cyklu sezení: ověřuje úplné vyčištění klientského stavu a návrat do anonymního režimu. |
| **LOG-07** | `test_login_navigation_to_register` | 1. Klik na odkaz `a[data-test="register_link"]` přesměruje na `/register`<br>2. Viditelnost pole `name_input`<br>3. Viditelnost pole `email_input`<br>4. Viditelnost pole `password_input`<br>5. Viditelnost pole `password_again_input` | Ověřuje funkční navigaci mezi přihlašovací a registrační obrazovkou. |
| **LOG-08** | `test_login_case_insensitive_and_trimmed_email` | 1. Zadání emailu s mezerami a velkými písmeny (`  LECTOR@LECTOR.COM  `)<br>2. Úspěšná autentizace a přesměrování<br>3. Ověření přihlášeného stavu v navigaci | Splňuje kritérium US-03: systém je tolerantní k velikosti písmen a automaticky ořezává mezery. |

---

### Oblast 4: Úvodní navigační rozcestník (Modul 0: US-01)

| ID testu | Název testu | Prováděné kontroly (Asserts) | Proč je kontrola dostatečná |
| :--- | :--- | :--- | :--- |
| **POR-01** | `test_portal_navigation_links_present_and_valid` | 1. Titulek stránky obsahuje 'Testování'<br>2. Přítomny funkční odkazy na Kalkulačku, Testovací login, NextDate a Registraci na kurz (včetně výpisu)<br>3. Přítomen odkaz 'Demo-login' | Ověřuje kompletní navigační rozcestník portálu dle specifikace US-01. |
| **POR-02** | `test_portal_demo_login_link_navigates_to_courses` | 1. Klik na 'Demo-login' přesměruje na `/courses`<br>2. Načtení a zobrazení nadpisu katalogu kurzů | Ověřuje přímý vstup návštěvníka z rozcestníku do aplikace kurzů. |

---

### Oblast 5: Uživatelský profil (Modul 5: US-18)

| ID testu | Název testu | Prováděné kontroly (Asserts) | Proč je kontrola dostatečná |
| :--- | :--- | :--- | :--- |
| **PRF-01** | `test_profile_prefilled_with_customer_data` | 1. Formulář `/profile` předvyplní jméno a email přihlášeného zákazníka<br>2. Ověření shody načtených údajů | Ověřuje integritu zobrazení profilu (US-18). |
| **PRF-02** | `test_profile_update_ico_and_phone` | 1. Vyplnění platného IČO (27082440) a telefonu<br>2. Uložení a přesměrování na `/home`<br>3. Znovunačtení `/profile` a ověření perzistence | Ověřuje aktualizaci a perzistenci kontaktních a fakturačních údajů zákazníka. |
| **PRF-03** | `test_profile_navigation_from_menu` | 1. Klik na 'Můj Profil' v horní liště<br>2. Přesměrování na `/profile`<br>3. Zobrazení formuláře | Ověřuje dostupnost profilu z navigace. |

---

### Oblast 6: Moje kurzy (Modul 3: US-13)

| ID testu | Název testu | Prováděné kontroly (Asserts) | Proč je kontrola dostatečná |
| :--- | :--- | :--- | :--- |
| **MYC-01** | `test_my_courses_accessible_from_navigation` | 1. Přihlášení zákazníka<br>2. Klik na 'Moje kurzy' v navigaci<br>3. Přesměrování na `/my-courses` a načtení kontejneru | Ověřuje přístup k privátnímu přehledu zapsaných kurzů pro zákazníka (US-13). |

---

### Oblast 7: Obnova hesla (Forgot Password - US-05)

| ID testu | Název testu | Prováděné kontroly (Asserts) | Proč je kontrola dostatečná |
| :--- | :--- | :--- | :--- |
| **RST-01** | `test_navigation_from_login_to_forgot_password` | 1. Odkaz `a[data-test="forgot_password_link"]` je viditelný na `/login`<br>2. Přesměrování na `/forgot-password`<br>3. Zobrazení popisu `div[data-test="forget_password_p"]`<br>4. Přítomnost `input[data-test="email_input"]` a `button[data-test="submit_button"]`<br>5. Přítomnost navigace | Ověřuje funkční propojení a dostupnost formuláře pro obnovu přístupu. |
| **RST-02** | `test_forgot_password_empty_email_validation` | 1. URL zůstává na `/forgot-password`<br>2. Chybová hláška `"The email field is required."` v `span[data-test="email_input_errors"]` | Zabraňuje odeslání prázdné žádosti a ověřuje specifickou chybovou hlášku. |
| **RST-03** | `test_forgot_password_nonexistent_email_validation` | 1. URL zůstává na `/forgot-password`<br>2. Chybová hláška `"We can't find a user with that email address."`<br>3. Žádný pád serveru (žádná 500) | Ověřuje validaci identity uživatele a zamezuje odesílání emailů na neexistující účty. |
| **RST-04** | `test_forgot_password_registered_user_submission` | 1. Odeslání formuláře s emailem registrovaného uživatele odešle POST požadavek na backend<br>2. Backend vrátí platný status (200 OK nebo 422 při rate limiting)<br>3. Při rate limiting je uživatel kultivovaně informován (`"Please wait before retrying."`) bez pádu aplikace | End-to-end ověření komunikace s autentizačním backendem včetně ošetření throttling limitu. |

---

## 3. Závěr vyhodnocení

Všech **34 testů** splňuje nejpřísnější kritéria spolehlivého testování a plně reflektuje akceptační kritéria ze specifikace **Specifikace požadavků podle zdrojového kódu (User Stories)**:
- **Žádný test se nespoléhá pouze na URL adresu.**
- Všechny selektory využívají stabilní atributy **`data-test` a `data-testid`**.
- Všechny úspěšné stavy kontrolují změny v **DOM navigaci (menu)**, **přítomnost/absenci uživatelských prvků** i **přesné hodnoty formulářů**.
- Všechny negativní stavy kontrolují **přesné znění chybových hlášek** generovaných aplikací.
- Testy striktně ověřují **oddělení rolí (RBAC)** – rozlišují anonymního návštěvníka, běžného zákazníka i lektora se specifickými právy správy kurzů.
- Pokryty jsou všechny moduly: **Úvodní rozcestník (Modul 0)**, **Autentizace a sezení (Modul 1)**, **Katalog a detail kurzů (Modul 2)**, **Zápis a Moje kurzy (Modul 3)**, **Správa kurzů a běhů (Modul 4)** a **Uživatelský profil (Modul 5)**.
