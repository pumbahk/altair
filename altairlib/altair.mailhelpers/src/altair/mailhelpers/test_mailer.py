# encoding: utf-8

import unittest
import mock
from datetime import datetime
from pytz import UTC

class MailerTest(unittest.TestCase):
    @mock.patch('smtplib.SMTP')
    def test_it(self, SMTP):
        from .mailer import Mailer
        m = Mailer({
            'mail.message.encoding': 'ISO-2022-JP',
            'mail.host': 'localhost',
            'mail.port': 0,
            })
        m.create_message(
            sender='foo@example.com',
            recipient='bar@example.com',
            subject=u'題名',
            body=u'こんにちは',
            now=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
            )
        m.send('foo@example.com', 'bar@example.com')
        SMTP.assert_called_with('localhost', 0)
        msg = '''MIME-Version: 1.0
Content-Type: text/plain; charset="iso-2022-jp"
Content-Transfer-Encoding: 7bit
Subject: =?iso-2022-jp?b?GyRCQmpMPhsoQg==?=
From: foo@example.com
To: bar@example.com
Date: Thu, 01 Jan 1970 00:00:00 -0000

\x1b$B$3$s$K$A$O\x1b(B'''
        SMTP.return_value.sendmail.assert_called_with('foo@example.com', 'bar@example.com', msg)
        SMTP.return_value.close.assert_called_once_with()


