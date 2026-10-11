import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_reset_email(user_email, reset_url):
    """Sends real email via SMTP if credentials are configured; logs link as fallback."""
    subject = "ProResume - Password Reset Request"
    body = f"""Hello,

You requested a password reset for your ProResume account.
Click the following link to reset your password (valid for 30 minutes):

{reset_url}

If you did not request this, please ignore this email.

Best regards,
The ProResume Team
"""
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = current_app.config.get('MAIL_PORT', 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER') or mail_username or 'noreply@proresume.com'

    if mail_username and mail_password:
        try:
            msg = MIMEMultipart()
            msg['From'] = mail_sender
            msg['To'] = user_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(mail_server, mail_port, timeout=10)
            if mail_use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
            server.quit()
            print(f"[EMAIL SENT] Password reset sent to {user_email}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email via SMTP: {e}")
            print(f"[FALLBACK RESET LINK]: {reset_url}")
            return False
    else:
        # Development fallback: Log link to console for immediate testing
        print("\n" + "="*60)
        print(" [LOCAL DEV] PASSWORD RESET LINK GENERATED:")
        print(f" User: {user_email}")
        print(f" URL:  {reset_url}")
        print("="*60 + "\n")
        return True
