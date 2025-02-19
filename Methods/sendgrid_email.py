import smtplib
from email.mime.text import MIMEText
from django.conf import settings
from django.core.mail import send_mail as django_send_mail

WELCOME_EMAIL_SUBJECT = "Welcome to Event Radar"
WELCOME_EMAIL_BODY_TEMPLATE = "Thank you for signing up for Event Radar, {first_name}! We're excited to have you on board!"

def send_confirmation_email(user):
    subject = WELCOME_EMAIL_SUBJECT
    body = WELCOME_EMAIL_BODY_TEMPLATE.format(first_name=user.first_name)
    email = user.email

    friendly_sender = settings.DEFAULT_FROM_EMAIL
    if "locmem" in settings.EMAIL_BACKEND:
        return django_send_mail(subject, body, friendly_sender, [email])
    else:
        smtp_server = settings.EMAIL_HOST
        smtp_port = settings.EMAIL_PORT
        smtp_username = settings.EMAIL_HOST_USER
        smtp_password = settings.EMAIL_PASSWORD
        sender_email = settings.SERVER_EMAIL
  
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = friendly_sender
        message["To"] = email
  
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, email, message.as_string())
            return True
        except Exception as e:
            return False 