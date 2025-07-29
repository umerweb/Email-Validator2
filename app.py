from flask import Flask, render_template, request
import re
import dns.resolver
import smtplib
import socket

app = Flask(__name__)

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

def validate_email_syntax(email):
    return bool(EMAIL_REGEX.match(email))

def check_mx_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return sorted([(r.preference, r.exchange.to_text()) for r in answers])
    except Exception:
        return []

def check_mailbox(mx_hosts, email):
    from_address = "verify@example.com"
    for pref, mx in mx_hosts:
        try:
            with smtplib.SMTP(timeout=10) as server:
                server.connect(mx)
                server.helo()
                server.mail(from_address)
                code, _ = server.rcpt(email)
                if code in [250, 251]:
                    return "✅ Exists"
                elif code == 550:
                    return "❌ Does not exist"
                else:
                    return f"⚠️ Unknown ({code})"
        except (socket.timeout, smtplib.SMTPException):
            continue
    return "❌ Failed to connect"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        syntax_valid = validate_email_syntax(email)

        if not syntax_valid:
            result = {
                "email": email,
                "syntax": "❌ Invalid",
                "mx": "⛔ Not Checked",
                "smtp": "⛔ Not Checked"
            }
        else:
            domain = email.split('@')[1]
            mx_records = check_mx_record(domain)
            mx_result = "✅ Found" if mx_records else "❌ Not Found"
            smtp_result = check_mailbox(mx_records, email) if mx_records else "⛔ Skipped"
            result = {
                "email": email,
                "syntax": "✅ Valid",
                "mx": mx_result,
                "smtp": smtp_result
            }

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
