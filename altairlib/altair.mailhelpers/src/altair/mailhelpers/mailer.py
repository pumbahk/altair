# cencoding: utf-8

import smtplib
from datetime import datetime
from time import mktime
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate

__all__ = [
    'Mailer',
    ]

class Mailer(object):
    def __init__(self, settings):
        self.settings = settings

    def create_message(self,
                       sender=None,
                       recipient=None,
                       subject=None,
                       body=None,
                       html=None,
                       encoding=None,
                       now=None):

        encoding = encoding or self.settings['mail.message.encoding']
        if html:
            mime_type = 'html'
            mime_text = html
        else:
            mime_type = 'plain'
            mime_text = body

        if now is None:
            now = datetime.now()

        if isinstance(now, datetime):
            t = mktime(now.timetuple()) - mktime(datetime.utcfromtimestamp(0).timetuple())
        elif isinstance(now, (int, long, float)):
            t = float(now)
        else:
            raise TypeError('now must be either datetime.datetime or float')

        msg = MIMEText(mime_text.encode(encoding, 'ignore'), mime_type, encoding)
        msg['Subject'] = Header(subject, encoding)
        msg['From'] = sender
        msg['To'] = recipient
        msg['Date'] = formatdate(t)
        self.message = msg

    def send(self, from_addr, to_addr):
        smtp = smtplib.SMTP(self.settings['mail.host'], self.settings['mail.port'])
        smtp.sendmail(from_addr, to_addr, self.message.as_string())
        smtp.close()

