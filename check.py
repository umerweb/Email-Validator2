import smtplib
import socket

host = 'mx1.mail.icloud.com'  # Try with iCloud's MX
port = 25

ipv4_addr = socket.gethostbyname(host)
print(f"Connecting to {ipv4_addr}:{port}")

server = smtplib.SMTP(timeout=10)
server.set_debuglevel(1)
server.connect(ipv4_addr, port)
server.helo('example.com')
server.quit()
