import smtplib
from email.mime.text import MIMEText
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from EventRadarProject import urls
from Methods.CustomTokenGenerator import CustomTokenGenerator


#code by Ben & Modified by Carolyn

#Use html for the email where it contains link with specific token for user
RESET_EMAIL_SUBJECT= "Event Radar Password Reset Link"
#where this is for html
RESET_BODY_TEMPLATE = """Hello {first_name},
You requested to reset the password for your account for this email address. Click the link:
{reset_link}

Sincerely,
The Event Radar Team""" #put the html for this in here

def send_reset_email(request, user):
    # Generates user token and uid
    token_generator = CustomTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = request.get_host()

    # Generate password reset link
    reset_link = f"{request.scheme}://{domain}{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
    subject = RESET_EMAIL_SUBJECT
    body = RESET_BODY_TEMPLATE.format(first_name=user.first_name, reset_link=reset_link)
    email = user.email

    print(f"Generated UID: {uid}")
    print(f"Generated Token: {token}")
    print(f"Generated Reset Link: {reset_link}")

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