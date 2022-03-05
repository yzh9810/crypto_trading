import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Configs import NotificationConfig, GeneralConfig
from Utils.Logger import *
from Utils import TimeHelper
import traceback
import asyncio

class Mailer:
    def __init__(self):
        pass

    async def sendMail(self, subject, body):
        if GeneralConfig.MODE == "dev":
            return
        userName = NotificationConfig.SENDER_EMAIL
        passWord = NotificationConfig.SENDER_EMAIL_PASSWORD
        adminList = NotificationConfig.ADMIN_EMAIL_LIST
        
        receiverEmail = None
        ccList = None
        if len(adminList) == 0:
            return

        if len(adminList) > 1:
            receiverEmail = adminList[0]
            ccList = adminList[1:]
        else:
            receiverEmail = adminList[0]
            ccList = []

        message = MIMEMultipart()
        message["From"] = userName
        message["To"] = receiverEmail
        if len(ccList) > 0:
            message["Cc"] = ','.join(ccList)  # Recommended for mass emails
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        try:
            smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo()
            smtpserver.login(userName, passWord)
            smtpserver.sendmail(userName, adminList, message.as_string())
        except:
            errorLogger = Logger("ErrEmail")
            errorLogger.logSyncFile(
                "errMail-" + str(TimeHelper.getCurrentTimestamp()),
                traceback.format_exc()
            )

# class DayCommodoresMailer:
#     def __init__(self, loop, commodores):
#         self.mailer = Mailer()
#         self.commodores = commodores
#         self.errorLogger = Logger("ErrEmail")
#         loop.create_task(self.dayMailingRoutine())
#
#     async def dayMailingRoutine(self):
#         await asyncio.sleep(5)
#         while True:
#             try:
#                 self.mailer.sendMail("Daily Report", "")
#             except:
#                 self.errorLogger.logSyncFile("mailerr", "")