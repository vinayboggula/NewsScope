from app.services.email import send_email

response = send_email(
    subject="PulseAI Test Email",
    body_text="This is a test email from PulseAI.",
    body_html="""
        <h1>PulseAI</h1>
        <p>This is a test email.</p>
        <p>Resend is working correctly! </p>
    """,
    recipients=["vinayboggula27@gmail.com"]
)

print(response)
