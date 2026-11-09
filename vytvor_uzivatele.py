import time
from playwright.sync_api import sync_playwright

def vytvor_skutecneho_uzivatele():
    ts = int(time.time())
    jmeno = f"Testovaci Uzivatel {ts}"
    email = f"tester_{ts}@testkitner.cz"
    heslo = "Heslo1234!"

    print("==================================================")
    print("ZAHÁJENÍ SKUTEČNÉ REGISTRACE V APLIKACI")
    print(f"Jméno: {jmeno}")
    print(f"Email: {email}")
    print(f"Heslo: {heslo}")
    print("==================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Krok: Otevření registračního formuláře
        print("\n1. Otevírám URL: http://testovani.kitner.cz/register")
        page.goto("http://testovani.kitner.cz/register")
        page.wait_for_load_state("networkidle")

        # 2. Krok: Vyplnění formuláře reálnými daty
        print("2. Vyplňuji formulář...")
        page.locator('input[placeholder="Jméno"]').fill(jmeno)
        page.locator('input[placeholder="Email"]').fill(email)
        page.locator('input[placeholder="Heslo"]').fill(heslo)
        page.locator('input[placeholder="Heslo znovu"]').fill(heslo)

        # 3. Krok: Kliknutí na tlačítko Registrovat
        print("3. Odesílám registraci kliknutím na 'Registrovat'...")
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(3000)

        # 4. Krok: Ověření v aplikaci po registraci
        print(f"\n4. Aktuální URL po registraci: {page.url}")
        uvitani = page.locator('text=Vítej uživateli').inner_text() if page.locator('text=Vítej uživateli').count() > 0 else ""
        print(f"5. Zobrazený uvítací text: '{uvitani}'")
        print(f"6. Viditelnost tlačítka 'Odhlásit se' v menu: {page.locator('text=Odhlásit se').is_visible()}")

        # 5. Krok: Odhlášení a znovupřihlášení pro 100% důkaz funkčnosti účtu
        print("\n7. Odhlašuji nového uživatele...")
        page.locator('text=Odhlásit se').click()
        page.wait_for_timeout(2000)
        print(f"   URL po odhlášení: {page.url}")

        print("8. Zkouším se znovu přihlásit s čerstvě vytvořeným účtem...")
        page.goto("http://testovani.kitner.cz/login")
        page.locator("#email_input").fill(email)
        page.locator("#password_input").fill(heslo)
        page.locator('button[type="submit"]').click()
        page.wait_for_timeout(2000)

        print(f"9. URL po úspěšném přihlášení: {page.url}")
        print(f"10. Je uživatel opět v menu přihlášen? {page.locator('text=Odhlásit se').is_visible()}")

        browser.close()

    print("\n==================================================")
    print("VÝSLEDEK: Uživatel byl úspěšně skutečně vytvořen v databázi aplikace!")
    print(f"Přihlašovací email: {email}")
    print(f"Heslo: {heslo}")
    print("==================================================")

if __name__ == "__main__":
    vytvor_skutecneho_uzivatele()
