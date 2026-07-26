from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.templates.otp_email import otp_template


class EmailService:

    @staticmethod
    async def send_email(
        recipient: str,
        subject: str,
        html: str,
    ) -> None:
        message = EmailMessage()

        message["From"] = settings.BREVO_FROM_EMAIL
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content("Please enable HTML to view this email.")
        message.add_alternative(html, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=settings.BREVO_SMTP_HOST,
            port=settings.BREVO_SMTP_PORT,
            username=settings.BREVO_SMTP_USERNAME,
            password=settings.BREVO_SMTP_PASSWORD,
            start_tls=True,
        )

    @staticmethod
    async def send_otp(
        recipient: str,
        username: str,
        otp: str,
    ) -> None:
        await EmailService.send_email(
            recipient=recipient,
            subject="Verify your WebX account",
            html=otp_template(
                username=username,
                otp=otp,
            ),
        )
