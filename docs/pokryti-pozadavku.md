# Analýza pokrytí funkcionality aplikace v požadavcích

Tento dokument porovnává reálnou funkcionalitu nalezenou ve zdrojových kódech aplikace v adresáři `app_src/kitner` vůči evidovaným požadavkům a manuálním test casům v adresáři `docs/`.

---

## 1. Shrnutí stavu

* **Zdrojové kódy (`app_src/kitner`):** Obsahují celkem **19 identifikovaných uživatelských a servisních funkcionalit** rozdělených mezi 3 role (Návštěvník / Guest, Zákazník / Student, Lektor / Organizátor) a servisní endpointy.
* **Evidované požadavky v `docs/`:** Aktuálně jsou v dokumentaci popsány pouze **2 User Stories** s manuálními test casy:
  * `docs/testcases/TC_US04_zapis_na_kurz.md` (US04 – Přihlášení studenta na termín kurzu)
  * `docs/testcases/TC_US13_moje_kurzy.md` (US13 – Zobrazení přihlášených kurzů / Moje kurzy)
* **Výsledek porovnání:** **15 z 19 funkcionalit (cca 79 %)** nemá v adresáři `docs/` sepsané žádné požadavky ani akceptační kritéria.

---

## 2. Přehledová tabulka pokrytí funkcionalit v požadavcích

| ID | Modul / Funkcionalita | Oprávněná role | Zdrojové soubory v `app_src/kitner` | Pokryto v `docs/` | Stav požadavku | Pokryto v `tests/` |
|:---|:---|:---:|:---|:---:|:---|:---:|
| **F01** | **Prohlížení katalogu kurzů** (`/courses`) | Host, Zákazník, Lektor | `CourseController.php` (`index`)<br>`Courses.jsx` | ⚠️ Částečně | Zmíněno jako precondice v US04, chybí samostatná US pro katalog | ✅ `test_courses.py` |
| **F02** | **Detail kurzu a zobrazení termínů** (`/courses/:id`) | Host, Zákazník, Lektor | `CourseController.php` (`show`)<br>`CourseDetail.jsx` | ⚠️ Částečně | Zmíněno v krocích US04, chybí samostatná US pro detail | ✅ `test_courses.py` |
| **F03** | **Nezávazná registrace na termín kurzu** (`/courses/:id/register`) | Zákazník (`customer`) | `CourseController.php` (`enroll`)<br>`CourseRegistration.jsx` | ✅ **ANO** | **Plně pokryto v US04** (`TC_US04_zapis_na_kurz.md`) | ✅ `test_courses.py` |
| **F04** | **Zobrazení sekce Moje kurzy** (`/my-courses`) | Zákazník (`customer`) | `CourseController.php` (`indexMyCourses`)<br>`MyCourses.jsx` | ✅ **ANO** | **Plně pokryto v US13** (`TC_US13_moje_kurzy.md`) | ✅ `test_my_courses.py` |
| **F05** | **Vytvoření nového kurzu** (`/courses/create`) | Pouze Lektor (`lector`, role 2) | `CourseController.php` (`store`)<br>`CreateCourse.jsx` | ❌ **NE** | **Chybí v požadavcích** (specifikace tvorby kurzu, cena, kapacita, poměr stran obrázku 600:338) | ❌ Chybí test |
| **F06** | **Vypsání nového běhu / termínu kurzu** (`/courses/:id/create-iteration`) | Pouze Lektor (`lector`, role 2) | `CourseController.php` (`storeIteration`)<br>`CreateCourseIteration.jsx` | ❌ **NE** | **Chybí v požadavcích** (datum od/do, den v týdnu, čas konání, forma/místo) | ❌ Chybí test |
| **F07** | **Zobrazení seznamu přihlášených účastníků** (`/courses/:id/participants`) | Pouze Lektor (`lector`, role 2) | `CourseController.php` (`getEnrolledUsers`)<br>`CourseParticipants.jsx` | ❌ **NE** | **Chybí v požadavcích** (přehled účastníků: jméno, e-mail, telefon, IČO) | ❌ Chybí test |
| **F08** | **Registrace nového uživatele** (`/register`) | Host (nepřihlášený) | `RegisteredUserController.php` (`store`)<br>`Register.jsx` | ❌ **NE** | **Chybí v požadavcích** (validační pravidla pro jméno, e-mail, shodu hesel) | ✅ `test_registration.py` |
| **F09** | **Přihlášení uživatele (Login)** (`/login`) | Host (nepřihlášený) | `AuthenticatedSessionController.php` (`store`)<br>`Login.jsx` | ❌ **NE** | **Chybí v požadavcích** (autentizace, chybové stavy špatných údajů) | ✅ `test_login.py` |
| **F10** | **Žádost o obnovu hesla** (`/forgot-password`) | Host, Zákazník | `PasswordResetLinkController.php` (`store`)<br>`ForgotPassword.jsx` | ❌ **NE** | **Chybí v požadavcích** (zadání e-mailu a odeslání resetovacího linku) | ✅ `test_forgot_password.py` |
| **F11** | **Nastavení nového hesla s tokenem** (`/password-reset/:token`) | Host (s tokenem) | `NewPasswordController.php` (`store`)<br>`ResetPassword.jsx` | ❌ **NE** | **Chybí v požadavcích** (resetovací formulář, token, nové heslo) | ❌ Chybí test |
| **F12** | **Ověření e-mailu odkazem** (`/verify-email/{id}/{hash}`) | Přihlášený uživatel | `VerifyEmailController.php`<br>`routes/auth.php` | ❌ **NE** | **Chybí v požadavcích** (verifikace e-mailové adresy) | ❌ Chybí test |
| **F13** | **Znovuzaslání verifikačního e-mailu** | Přihlášený uživatel | `EmailVerificationNotificationController.php`<br>`routes/auth.php` | ❌ **NE** | **Chybí v požadavcích** | ❌ Chybí test |
| **F14** | **Odhlášení z aplikace (Logout)** | Přihlášený uživatel | `AuthenticatedSessionController.php` (`destroy`)<br>`AuthLayout.jsx` | ❌ **NE** | **Chybí v požadavcích** (zrušení session, vyčištění tokenů) | ✅ `test_logout.py` |
| **F15** | **Úprava osobního profilu** (`/profile`) | Přihlášený uživatel | `UserController.php` (`updateProfile`)<br>`Profile.jsx` | ❌ **NE** | **Chybí v požadavcích** (editace jména, tel, IČO s modulo 11) | ✅ `test_profile.py` |
| **F16** | **Rozcestník projektů (Linktree)** (`/`) | Kdokoli | `Linktree.jsx`<br>`routes/web.php` | ❌ **NE** | **Chybí v požadavcích** (odkazy na Kalkulačku, Demo-login, NextDate atd.) | ✅ `test_portal.py` |
| **F17** | **Domovská uvítací stránka** (`/home`) | Přihlášený uživatel | `Home.jsx`<br>`App.jsx` | ❌ **NE** | **Chybí v požadavcích** (uvítací banner přihlášeného uživatele) | ✅ `test_navigation.py` |
| **F18** | **Servisní databázové migrace** (`/migrate`) | Servisní (kdokoli) | `routes/web.php` | ❌ **NE** | **Chybí v požadavcích** (technická routa pro spuštění `artisan migrate`) | ❌ Chybí test |
| **F19** | **Servisní pročištění cache** (`/clear-cache`) | Servisní (kdokoli) | `routes/web.php` | ❌ **NE** | **Chybí v požadavcích** (technická routa pro vymazání cache) | ❌ Chybí test |

---

## 3. Detailní rozbor nepopsaných oblastí v požadavcích

### 1. Modul Lektor / Organizátor (Zcela chybí v požadavcích i testech)
V kódu aplikace je plně implementována role lektora (`role_id = 2`), která disponuje rozsáhlou funkcionalitou, jež není v `docs/` vůbec zmíněna:
* **Tvorba nového kurzu (`F05`):** Validace názvu, popisu, kapacity a ceny. Klientská kontrola rozměrů nahrávaného obrázku kurzu (požadovaný poměr 600:338 s tolerancí 5 %).
* **Vypisování běhů kurzu (`F06`):** Plánování začátku a konce kurzu, výběr dne v týdnu, času a místa konání.
* **Evidence studentů (`F07`):** Možnost lektora zobrazit seznam všech přihlášených studentů na daný běh kurzu včetně jejich kontaktních údajů a IČO.
* **Ochrana přístupu:** Běžný zákazník ani nepřihlášený uživatel nesmí mít k těmto akcím přístup (backend vrací HTTP 403 Forbidden).

### 2. Autentizační a účtové toky (Chybí v požadavcích, existují automatizované testy)
V `tests/` sice existují automatizované testy pro přihlášení, odhlášení a registraci, ale v `docs/` k nim neexistují žádné sepsané User Stories ani akceptační kritéria:
* **Registrace (`F08`):** Chybí specifikace povinných polí, minimální délky hesel a formátu e-mailu.
* **Zapomenuté heslo a reset tokenem (`F10`, `F11`):** Chybí popis toku pro obnovu zapomenutého hesla přes e-mail a platnosti tokenu.
* **Ověření e-mailu (`F12`, `F13`):** Chybí popis procesu aktivace účtu.

### 3. Správa profilu (`F15`)
* V aplikaci je stránka `/profile` s formulářem na úpravu jména, telefonu a IČO.
* Kód implementuje přísnou klientskou i serverovou validaci IČO podle algoritmu kontrolního součtu modulo 11. Tato pravidla nejsou v dokumentaci popsána.

---

## 4. Doporučené kroky k doplnění dokumentace

Pro dosažení plné sledovatelnosti (Traceability) se doporučuje doplnit do `docs/testcases/` tyto chybějící User Stories:
1. **US – Správa kurzů lektorem:** Vytvoření kurzu, termínu a zobrazení účastníků.
2. **US – Registrace a správa účtu:** Registrace nového studenta a úprava profilu (včetně IČO validace).
3. **US – Přihlášení a obnova hesla:** Přihlášení, odhlášení a zapomenuté heslo.
4. **US – Prohlížení katalogu a detailu kurzu:** Zobrazení seznamu kurzů a jejich běhů bez nutnosti přihlášení.

