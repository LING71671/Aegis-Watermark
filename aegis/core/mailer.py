import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import formataddr

class Mailer:
    def __init__(self, smtp_server, smtp_port, sender_email, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.password = password

    def send_protected_file(self, recipient_email, file_path, subject, body):
        """发送带附件的个性化邮件"""
        try:
            message = MIMEMultipart()
            message['From'] = formataddr(("Aegis Distribution", self.sender_email))
            message['To'] = recipient_email
            message['Subject'] = Header(subject, 'utf-8')
            message.attach(MIMEText(body, 'plain', 'utf-8'))

            # 添加附件
            filename = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            message.attach(part)

            # 执行发送
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            return True
        except Exception as e:
            print(f"[ERROR] SMTP distribution failed for {recipient_email}: {e}")
            return False
