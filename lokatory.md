# Automatizace testování: Lokátory (data-test / data-testid)

Tento dokument obsahuje přehlednou tabulku všech použitých stabilních lokátorů (`data-test` a `data-testid`) pro testovací aplikaci **Demo login** ([http://testovani.kitner.cz](http://testovani.kitner.cz)).

Všechny Page Objecty v projektu byly refaktorovány tak, aby primárně využívaly tyto atributy, což zajišťuje maximální stabilitu a odolnost testů proti změnám CSS stylů nebo HTML struktury.

---

## 1. Horní navigace (Navbar)

| Element / Prvek | Selektor (data-test / data-testid) | Popis / Použití |
| :--- | :--- | :--- |
| **Kontejner navigace** | `[data-test="navigation"]` | Hlavní `<nav>` lišta záhlaví |
| **Brand / Domů (Kitner)** | `a[data-test="navigation_home_link"]` | Logo / odkaz na úvodní web |
| **Odkaz Kurzy** | `li[data-test="navigation_home_list_item"] a[data-test="courses_link"]` | Přechod do přehledu kurzů (`/courses`) |
| **Odkaz Domů** | `a[data-test="home_link"]` | Přechod na domovskou nástěnku (`/home`) |
| **Odkaz Moje kurzy** | `a[data-test="courses_link"]:has-text("Moje kurzy")` | Přechod na seznam zakoupených kurzů |
| **Odkaz Můj Profil** | `li[data-test="navigation_profile_item"] a[data-test="courses_profile"]` | Profil přihlášeného uživatele |
| **Tlačítko Přihlásit se** | `li[data-test="navigation_login_item"] a[data-test="login_link"]` | Odkaz na přihlašovací formulář (`/login`) |
| **Tlačítko Odhlásit se** | `li[data-test="navigation_logout_item"] a[data-test="logout_button"]` | Ukončení sezení a odhlášení uživatele |
| **Mobilní menu** | `div[data-test="hamburger_menu"]` | Tlačítko pro rozbalení mobilního menu |

---

## 2. Přihlašovací formulář (`/login`)

| Element / Prvek | Selektor (data-test / data-testid) | Popis / Použití |
| :--- | :--- | :--- |
| **Přihlašovací sekce** | `section[data-test="login_section"]` | Obalující sekce stránky přihlášení |
| **Nadpis formuláře** | `div[data-test="login_text"]` | Textový blok „Přihlášení“ |
| **Formulář** | `form[data-test="login_form"]` | Samotný `<form>` element |
| **Emailové pole** | `input[data-test="email_input"]` | Vstupní pole pro zadání emailu |
| **Heslo pole** | `input[data-test="password_input"]` | Vstupní pole pro zadání hesla |
| **Tlačítko Přihlásit** | `button[data-test="login_button"]` | Odesílací tlačítko formuláře |
| **Zapomněli jste heslo?** | `a[data-test="forgot_password_link"]` | Odkaz pro obnovení zapomenutého hesla |
| **Odkaz na registraci** | `a[data-test="register_link"]` | Odkaz „Zaregistrujte se zde.“ směřující na `/register` |

---

## 3. Registrační formulář (`/register`)

| Element / Prvek | Selektor (data-test / data-testid) | Popis / Použití |
| :--- | :--- | :--- |
| **Registrační sekce** | `section[data-test="register_section"]` | Obalující sekce stránky registrace |
| **Nadpis formuláře** | `div[data-test="register_text"]` | Textový blok „Registrace“ |
| **Formulář** | `form[data-test="register_form"]` | Samotný `<form>` element registrace |
| **Jméno pole** | `input[data-test="name_input"]` | Vstupní pole pro zadání celého jména |
| **Email pole** | `input[data-test="email_input"]` | Vstupní pole pro zadání emailu |
| **Heslo pole** | `input[data-test="password_input"]` | Vstupní pole pro heslo |
| **Heslo znovu pole** | `input[data-test="password_again_input"]` | Vstupní pole pro potvrzení hesla |
| **Tlačítko Registrovat**| `button[data-test="register_button"]` | Odesílací tlačítko registrace |
| **Odkaz na přihlášení** | `p[data-test="login_p"] a[data-test="login_link"]` | Odkaz „Přihlaste se zde.“ směřující na `/login` |

---

## 4. Přehled a správa kurzů (`/courses`)

| Element / Prvek | Selektor (data-test / data-testid) | Popis / Použití |
| :--- | :--- | :--- |
| **Sekce kurzů** | `div[data-test="courses_section"]` | Hlavní kontejner katalogu kurzů |
| **Nadpis stránky** | `h1[data-test="courses_title"]` | Nadpis „Seznam kurzů“ |
| **Tlačítko Přidat kurz (lektor)** | `button[data-test="registration_link"]:has-text("Přidat kurz")` | Tlačítko pro otevření modálu tvorby kurzu |
| **Tlačítko Přidat iteraci (lektor)**| `button[data-test="registration_link"]:has-text("Přidat iteraci")`| Tlačítko pro přidání termínu u kurzu |
| **Karty kurzů** | `div[data-test^="course_"]` | Jednotlivé karty (např. `course_1`, `course_2`...) |
| **Název kurzu** | `h2[data-test="course_name"]` | Nadpis / jméno kurzu na kartě |
| **Popis kurzu** | `p[data-test="course_description"]` | Popis kurzu na kartě |
| **Kapacita kurzu** | `p[data-test="course_capacity"]` | Počet míst (např. „Kapacita: 12“) |
| **Cena kurzu** | `p[data-test="course_price"]` | Cena kurzu (např. „Cena: 2490 Kč“) |
| **Detail kurzu** | `button[data-test="registration_link"]:has-text("Chci vidět více")` | Tlačítko pro detail a přihlášení na kurz |

---

## 5. Modální okno: Vytvořit kurz (Lektor)

| Element / Prvek | Selektor (data-test / data-testid) | Popis / Použití |
| :--- | :--- | :--- |
| **Kontejner modálu** | `div[data-test="course_form_container"]` | Celé vyskakovací okno modálu |
| **Nadpis modálu** | `h1[data-test="create_course_title"]` | Nadpis „Vytvořit kurz“ |
| **Formulář kurzu** | `form[data-test="course_form"]` | `<form>` uvnitř modálního okna |
| **Název kurzu pole** | `input[data-test="course_name_input"]` | Vstup pro název nového kurzu |
| **Popis kurzu pole** | `textarea[data-test="course_description_input"]`| Textarea pro anotaci kurzu |
| **Kapacita pole** | `input[data-test="course_capacity_input"]`| Číselný vstup pro kapacitu |
| **Cena pole** | `input[data-test="course_price_input"]` | Číselný vstup pro cenu v Kč |
| **Nahrání souboru** | `input[data-test="course_file_input"]` | File input pro obrázek/podklady |
| **Tlačítko Vytvořit kurz** | `div[data-test="course_form_submit_button_container"] button` | Odeslání a založení kurzu v systému |

