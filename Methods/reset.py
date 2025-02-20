import smtplib
from email.mime.text import MIMEText
from django.conf import settings
from django.core.mail import send_mail as django_send_mail

