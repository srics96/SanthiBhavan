from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEImage import MIMEImage

from celery.decorators import task

from django.conf import settings
from django.core.mail import send_mail

import _constants
import smtplib


@task(name="dispatch_email")
def dispatch_email(subject, message, recipient, html_message=None):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = _constants.SYSTEM_MAIL
    msg['To'] = recipient
    server = smtplib.SMTP_SSL('smtp.zoho.com', 465)
    server.login(_constants.SYSTEM_MAIL, _constants.SYSTEM_MAIL_PASSWORD)
    if html_message:
    	server.sendmail(_constants.SYSTEM_MAIL, [recipient], msg.as_string(), html_message=html_message)
    else:
    	server.sendmail(_constants.SYSTEM_MAIL, [recipient], msg.as_string())
    server.quit()

@task(name="send_invoice")
def send_invoice(invoice_dict, message):
    server = smtplib.SMTP_SSL('smtp.zoho.com', 465)
    server.login(_constants.SYSTEM_MAIL, _constants.SYSTEM_MAIL_PASSWORD)
    subject = "Invoice for Booking at Hotel Santhi Bhavan"
    recipient = invoice_dict['email']
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = _constants.SYSTEM_MAIL
    msg['To'] = recipient
    html_payload = MIMEText(message, 'html')
    msg.attach(html_payload)
    server.sendmail(_constants.SYSTEM_MAIL, recipient, msg.as_string())
    server.quit()


    

    
    
    
    