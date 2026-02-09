import smtplib
import ssl
import sys

def debug_smtp():
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    sender = "2422366956@qq.com"
    password = "dopllzpzvpnadihg"
    
    print(f"[*] Attempting to connect to {smtp_server}:{smtp_port}...")
    context = ssl.create_default_context()
    try:
        # 使用 SMTP_SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=10) as server:
            server.set_debuglevel(1)
            print("[*] Connected. Logging in...")
            server.login(sender, password)
            print("[*] Login successful!")
            return True
    except Exception as e:
        print(f"[!] SMTP Error: {e}")
        return False

if __name__ == "__main__":
    if debug_smtp():
        print("DIAGNOSTIC_SUCCESS")
    else:
        print("DIAGNOSTIC_FAILED")
        sys.exit(1)
