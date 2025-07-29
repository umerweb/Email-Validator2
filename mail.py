import smtplib
import dns.resolver
import socket
import re

def get_mx(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = sorted([(r.preference, str(r.exchange).rstrip('.')) for r in answers])
        print(f"✅ MX records for {domain}: {mx_records}")
        return mx_records
    except Exception as e:
        print(f"❌ MX lookup failed for {domain}: {e}")
        return []

def verify_email(email, from_address='umer.web2@gmail.com'):
    print(f"\n🔍 Verifying: {email}")
    
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return "❌ Invalid syntax"

    domain = email.split('@')[-1]
    mx_records = get_mx(domain)
    if not mx_records:
        return "❌ No MX records found."

    for _, mx in mx_records:
        try:
            print(f"🔌 Connecting to {mx}...")
            server = smtplib.SMTP(timeout=10)
            server.connect(mx)
            server.helo('yourdomain.com')
            server.mail(from_address)
            code, message = server.rcpt(email)
            server.quit()

            print(f"📩 SMTP response: {code} - {message.decode()}")

            if code == 250 or code == 251:
                return "✔️ Valid email (SMTP server accepted RCPT)"
            elif code == 550:
                return f"❌ Rejected: User does not exist ({message.decode()})"
            else:
                return f"⚠️ Response unclear: {code} - {message.decode()}"
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, socket.timeout) as e:
            return f"❌ Connection failed to {mx}: {e}"
        except Exception as e:
            return f"❌ Error during SMTP check: {e}"

    return "❌ All MX servers failed."

# Example usage
email_to_check = 'vorphix@gmail.com'
result = verify_email(email_to_check)
print(f"\n✅ Final Result: {result}")
