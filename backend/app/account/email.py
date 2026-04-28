# app/account/email.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config
from fastapi import HTTPException

SMTP_HOST = config("SMTP_HOST", default="smtp.gmail.com")
SMTP_PORT = config("SMTP_PORT", cast=int, default=587)
SMTP_USER = config("SMTP_USER", default="timamolchanov885@gmail.com")
SMTP_PASSWORD = config("SMTP_PASSWORD", default="gkznancoingifuyl")
FROM_EMAIL = config("FROM_EMAIL", default="timamolchanov885@gmail.com")


async def send_verification_email(to_email: str, token: str):
    """Отправляет письмо с ссылкой подтверждения email"""
    frontend_url = config("FRONTEND_URL", default="http://localhost:3000")
    verify_link = f"{frontend_url}/verify-email?token={token}"

    msg = MIMEMultipart("alternative")
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Подтверждение email адреса"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Добро пожаловать!</h2>
        <p>Для завершения регистрации подтвердите ваш email адрес:</p>
        <p style="margin: 20px 0;">
            <a href="{verify_link}" 
               style="background-color: #7c3aed; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 6px; font-weight: bold;">
                Подтвердить email
            </a>
        </p>
        <p>Ссылка действительна в течение 1 часа.</p>
        <p>Если вы не регистрировались — проигнорируйте это письмо.</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Письмо подтверждения отправлено на {to_email}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки email: {e}")
        raise HTTPException(
            status_code=500, detail="Не удалось отправить письмо. Попробуйте позже."
        )
