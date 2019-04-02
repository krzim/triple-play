from apps import App, action
import smtplib
import email.utils
from email.mime.text import MIMEText
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class EmailSender(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def send_email(self, sender, receivers, subject, message, html, sender_name, username, password, ip, port):
        server = smtplib.SMTP('{0}:{1}'.format(ip, port))
        try:
            server.set_debuglevel(False)
            server.ehlo()
            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()  # re-identify ourselves over TLS connection
            server.login(username, password)
        except Exception as e:
            shutdown(ip, port)

        message_format = 'html' if html else 'plain'
        msg = MIMEText(message, message_format)
        msg.set_unixfrom('author')
        msg['To'] = email.utils.formataddr(('Recipient', receivers))
        msg['From'] = email.utils.formataddr((sender_name, sender))
        msg['Subject'] = subject
        server.sendmail(sender, receivers, msg.as_string())
        return 'success'

    def shutdown(self, ip, port):
        server = smtplib.SMTP('{0}:{1}'.format(ip, port))
        server.quit()
