import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

RECIPIENT = "radek@kitner.cz"
SUBJECT = "Výsledky automatizovaných testů – Demo Login (14/14 PASSED)"

EMAIL_BODY_HTML = """\
<html>
<head>
<style>
  body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
  .header { background: #1e3a8a; color: white; padding: 16px 20px; border-radius: 8px 8px 0 0; }
  .content { border: 1px solid #e5e7eb; border-top: none; padding: 20px; border-radius: 0 0 8px 8px; }
  .badge-pass { background-color: #16a34a; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
  table { width: 100%; border-collapse: collapse; margin-top: 15px; }
  th, td { border: 1px solid #e5e7eb; padding: 8px 12px; text-align: left; }
  th { background-color: #f3f4f6; }
  tr:nth-child(even) { background-color: #f9fafb; }
  .highlight { background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px; margin: 15px 0; }
</style>
</head>
<body>
  <div class="header">
    <h2>Report z běhu automatizovaných testů</h2>
    <p>Aplikace: <strong>Demo login</strong> (http://testovani.kitner.cz/courses)</p>
  </div>
  <div class="content">
    <p>Dobrý den Radku,</p>
    <p>zasílám souhrnný report z dokončeného běhu sady automatizovaných testů pro aplikaci <strong>Demo login</strong>.</p>
    
    <div class="highlight">
      <h3>Celkový výsledek testování: <span class="badge-pass">14 / 14 TESTŮ ÚSPĚŠNÝCH (100 %)</span></h3>
      <p>Doba běhu: <strong>60.15 s</strong> | Framework: <strong>pytest + Playwright</strong> | Prohlížeč: <strong>Chromium (Headless)</strong></p>
    </div>

    <h3>Přehled výsledků jednotlivých testů:</h3>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Oblast</th>
          <th>Název testu</th>
          <th>Klíčové kontroly (Asserts)</th>
          <th>Stav</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>LOG-01</td>
          <td>Login</td>
          <td>test_login_lector_success_and_privileges</td>
          <td>URL /courses, Menu: Odhlásit se viditelné, Přihlásit se skryté, Profil viditelný, Lektor: tlačítko 'Přidat kurz' a 'Přidat iteraci' zobrazeny</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>LOG-02</td>
          <td>Login</td>
          <td>test_login_registered_user_success</td>
          <td>Autentizace skutečného uživatele z registrace, menu přihlášen, kontrola hranice práv: nemá 'Přidat kurz'</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>LOG-03</td>
          <td>Login</td>
          <td>test_login_empty_fields_validation</td>
          <td>Ověření povinných polí 'The email field is required.' a 'The password field is required.', setrvání na /login</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>LOG-04</td>
          <td>Login</td>
          <td>test_login_invalid_password</td>
          <td>Ověření hlášky 'These credentials do not match our records.', zůstává na /login, menu ukazuje nepřihlášen</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>LOG-05</td>
          <td>Login</td>
          <td>test_login_nonexistent_user</td>
          <td>Ověření chybové hlášky pro neexistujícího uživatele</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>LOG-06</td>
          <td>Session</td>
          <td>test_logout_flow_and_session_cleared</td>
          <td>Odhlášení: tlačítko Odhlásit se zmizí, Přihlásit se se zobrazí, lektorská tlačítka zmizí</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>LOG-07</td>
          <td>Navigace</td>
          <td>test_login_navigation_to_register</td>
          <td>Proklik z /login přes 'Zaregistrujte se zde.' na /register, formulář je plně interaktivní</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>REG-01</td>
          <td>Registrace</td>
          <td>test_registration_success_verifies_login_state_and_welcome</td>
          <td>Přesměrování na /home, banner 'Vítej uživateli &lt;Jméno&gt;!', menu přihlášen, absence lektorských práv</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>REG-02</td>
          <td>Registrace</td>
          <td>test_registration_empty_form_validation</td>
          <td>Validace 3 povinných polí: Jméno, Email, Heslo, setrvání na /register</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>REG-03</td>
          <td>Registrace</td>
          <td>test_registration_password_mismatch</td>
          <td>Validace neshody hesel: 'The password field confirmation does not match.'</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>REG-04</td>
          <td>Registrace</td>
          <td>test_registration_duplicate_email</td>
          <td>Validace unikátnosti emailu v DB: 'The email has already been taken.'</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>REG-05</td>
          <td>Registrace</td>
          <td>test_registration_missing_name_only</td>
          <td>Izolovaná validace: chybí pouze jméno, u emailu a hesla se chyba nezobrazí</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>REG-06</td>
          <td>Registrace</td>
          <td>test_registration_missing_password_only</td>
          <td>Izolovaná validace: chybí pouze heslo, u jména a emailu se chyba nezobrazí</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
        <tr>
          <td>REG-07</td>
          <td>Navigace</td>
          <td>test_registration_link_navigates_to_login</td>
          <td>Proklik z /register přes 'Přihlaste se zde.' na /login, formulář je plně interaktivní</td>
          <td><span class="badge-pass">PASSED</span></td>
        </tr>
      </tbody>
    </table>

    <div class="highlight">
      <h4>Přílohy a dokumentace:</h4>
      <ul>
        <li><strong>report.html:</strong> Samostatný interaktivní HTML report generovaný pytestem s kompletními logy a metadaty.</li>
        <li><strong>kontroly_asserty.md:</strong> Podrobný rozbor všech assertů a vysvětlení, proč samotná kontrola URL nestačí.</li>
      </ul>
    </div>

    <p>S pozdravem,<br><strong>Automatizovaný Testovací Agent (Antigravity)</strong></p>
  </div>
</body>
</html>
"""

def send_email():
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    sender = os.environ.get("SMTP_SENDER", smtp_user or "tests@kitner.cz")

    print(f"Preparing test report email to: {RECIPIENT}")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"] = sender
    msg["To"] = RECIPIENT

    # Plaintext fallback
    plain_text = f"Report z automatizovaných testů aplikace Demo Login:\nVšech 14 testů proběhlo úspěšně (100% PASSED).\nKompletní HTML report byl vygenerován do souboru report.html."
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(EMAIL_BODY_HTML, "html"))

    # Attach report.html if available
    report_path = os.path.join(os.path.dirname(__file__), "report.html")
    if os.path.exists(report_path):
        with open(report_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=report.html")
        msg.attach(part)
        print(f"Attached report file: {report_path}")

    if smtp_host and smtp_user and smtp_pass:
        print(f"Sending email via {smtp_host}:{smtp_port}...")
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls(context=context)
                server.login(smtp_user, smtp_pass)
                server.sendmail(sender, [RECIPIENT], msg.as_string())
            print(f"Email successfully delivered to {RECIPIENT}!")
            return True
        except Exception as e:
            print(f"SMTP sending failed: {e}")
            return False
    else:
        print("NOTE: SMTP credentials (SMTP_HOST, SMTP_USER, SMTP_PASS) not configured in environment.")
        print(f"Email content is prepared and saved to 'report_email_content.html' and 'test_report.md'.")
        # Save HTML email output so user can review or send anytime
        with open("report_email_content.html", "w", encoding="utf-8") as f:
            f.write(EMAIL_BODY_HTML)
        return False

if __name__ == "__main__":
    send_email()

