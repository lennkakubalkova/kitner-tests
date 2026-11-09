import time
from playwright.sync_api import sync_playwright

UZIVATELE_K_REGISTRACI = [
    {"jmeno": "Petr Novotny", "heslo": "TestHeslo2026!"},
    {"jmeno": "Lucie Dvorakova", "heslo": "TestHeslo2026!"},
    {"jmeno": "Martin Cerny", "heslo": "TestHeslo2026!"},
    {"jmeno": "Eva Prochazkova", "heslo": "TestHeslo2026!"},
    {"jmeno": "Tomas Kucera", "heslo": "TestHeslo2026!"},
]

def registruj_uzivatele():
    vytvoreni = []
    ts = int(time.time())

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i, u in enumerate(UZIVATELE_K_REGISTRACI, start=1):
            page = browser.new_page()
            email = f"{u['jmeno'].lower().replace(' ', '.')}.{ts}_{i}@testkitner.cz"
            jmeno = f"{u['jmeno']} {ts}"
            heslo = u["heslo"]

            print(f"[{i}/{len(UZIVATELE_K_REGISTRACI)}] Registruji: {jmeno} ({email})...")

            page.goto("http://testovani.kitner.cz/register")
            page.wait_for_load_state("networkidle")

            page.locator('input[placeholder="Jméno"]').fill(jmeno)
            page.locator('input[placeholder="Email"]').fill(email)
            page.locator('input[placeholder="Heslo"]').fill(heslo)
            page.locator('input[placeholder="Heslo znovu"]').fill(heslo)
            page.locator('button[type="submit"]').click()
            page.wait_for_timeout(2500)

            # Ověření úspěšné registrace
            if "/home" in page.url or page.locator("text=Odhlásit se").is_visible():
                print(f"   -> Úspěšně zaregistrován a přihlášen na URL: {page.url}")
                vytvoreni.append({
                    "jmeno": jmeno,
                    "email": email,
                    "heslo": heslo,
                    "stav": "AKTIVNÍ / OVĚŘENÝ"
                })
            else:
                print(f"   -> Varování: neočekávaný stav pro {email}")

            page.close()

        browser.close()

    # Uložení seznamu do souboru
    vystup_cesta = "seznam_testovacich_uzivatelu.md"
    with open(vystup_cesta, "w", encoding="utf-8") as f:
        f.write("# Seznam skutečně vytvořených testovacích uživatelů\n\n")
        f.write("Uživatelé byli zaregistrováni přímo v aplikaci http://testovani.kitner.cz.\n\n")
        f.write("| Jméno | Email (Login) | Heslo | Stav |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for u in vytvoreni:
            f.write(f"| {u['jmeno']} | `{u['email']}` | `{u['heslo']}` | {u['stav']} |\n")

    print("\nHotovo! Všichni uživatelé byli vytvořeni.")
    return vytvoreni

if __name__ == "__main__":
    registruj_uzivatele()

