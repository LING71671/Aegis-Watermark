import smtplib
import ssl
import sys

def debug_smtp_587():
    smtp_server = "smtp.qq.com"
    smtp_port = 587
    sender = "2422366956@qq.com"
    password = "dopllzpzvpnadihg"
    
    print(f"[*] Attempting to connect to {smtp_server}:{smtp_port} (STARTTLS)...")
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.set_debuglevel(1)
        server.starttls(context=context)
        print("[*] TLS started. Logging in...")
        server.login(sender, password)
        print("[*] Login successful!")
        server.quit()
        return True
    except Exception as e:
        print(f"[!] SMTP Error: {e}")
        return False

if __name__ == "__main__":
    if debug_smtp_587():
        print("DIAGNOSTIC_SUCCESS")
    else:
        print("DIAGNOSTIC_FAILED")
