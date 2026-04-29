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


async def send_verification_email(to_email: str, token: str, verification_code: str):
    """Отправляет письмо с кодом подтверждения email"""

    msg = MIMEMultipart("alternative")
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Подтверждение email адреса"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2563eb;">Добро пожаловать!</h2>
        <p>Для завершения регистрации введите код подтверждения в приложении.</p>
        <p style="margin-top: 30px; font-size: 14px;">
            <strong>Ваш код подтверждения:</strong>
        </p>
        <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
            <p style="font-size: 48px; font-weight: bold; color: #7c3aed; margin: 0; letter-spacing: 4px;">
                {verification_code}
            </p>
        </div>
        <p style="color: #666; margin: 20px 0;">
            Код действителен в течение <strong>1 часа</strong>.
        </p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        <p style="font-size: 12px; color: #9ca3af;">
            Если вы не регистрировались, проигнорируйте это письмо.
        </p>
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
        print(
            f"✅ Письмо подтверждения отправлено на {to_email} с кодом {verification_code}"
        )
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки email: {e}")
        raise HTTPException(
            status_code=500, detail="Не удалось отправить письмо. Попробуйте позже."
        )
