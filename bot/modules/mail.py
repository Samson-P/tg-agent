import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

EMAIL_TEMPLATE = """\
Привет!
{message_body}

С уважением,
Виртуальный помощник Самсона,
Генри
"""


def send_email(to_email: str, subject: str, body: str):
    load_dotenv()

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    full_body = EMAIL_TEMPLATE.format(message_body=body)

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(full_body, "plain"))

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())

    print("Письмо успешно отправлено!")

# Пример использования
if __name__ == "__main__":
    send_email(
        to_email="recipient@example.com",
        subject="Тестовое письмо",
        body="Привет! Это письмо отправлено из Python скрипта через SMTP Яндекс."
    )

