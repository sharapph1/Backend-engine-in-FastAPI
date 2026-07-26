import asyncio

from app.services.email_service import EmailService


async def main():
    await EmailService.send_email(
        recipient="shashankrpatil777@gmail.com",
        subject="WebX Test",
        html="""
        <h1>WebX</h1>
        <p>If you're reading this, Brevo SMTP is working 🎉</p>
        """,
    )


asyncio.run(main())