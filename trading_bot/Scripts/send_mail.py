import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Configs import NotificationConfig

def sendMail(subject, body):
    username = NotificationConfig.SENDER_EMAIL
    password = NotificationConfig.SENDER_EMAIL_PASSWORD

    receiverEmail = None
    ccList = None

    if len(NotificationConfig.ADMIN_EMAIL_LIST) > 1:
        receiverEmail = NotificationConfig.ADMIN_EMAIL_LIST[0]
        ccList = NotificationConfig.ADMIN_EMAIL_LIST[1:]
    else:
        receiverEmail = NotificationConfig.ADMIN_EMAIL_LIST[0]
        ccList = []

    message = MIMEMultipart()
    message["From"] = username
    message["To"] = receiverEmail
    if len(ccList) > 0:
        message["Cc"] = ','.join(ccList)  # Recommended for mass emails
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(username, password)
    smtpserver.sendmail(username, NotificationConfig.ADMIN_EMAIL_LIST, message.as_string())

subject = "Testing"
body = "Testing\nTesting\nTesting"
sendMail(subject, body)