import os

import resend
from dotenv import load_dotenv


load_dotenv()


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")

if not RESEND_API_KEY:
    raise ValueError("RESEND_API_KEY is not set in .env")

if not EMAIL_FROM:
    raise ValueError("EMAIL_FROM is not set in .env")

resend.api_key = RESEND_API_KEY


def send_email(
    subject: str,
    body_text: str,
    body_html: str | None = None,
    recipients: list[str] | None = None,
):
    if not recipients:
        raise ValueError("At least one recipient email is required")

    params = {
        "from": EMAIL_FROM,
        "to": recipients,
        "subject": subject,
        "text": body_text,
    }

    if body_html:
        params["html"] = body_html

    print("SENDING TO:", recipients)
    print("SENDING FROM:", EMAIL_FROM)

    response = resend.Emails.send(params)

    return response
