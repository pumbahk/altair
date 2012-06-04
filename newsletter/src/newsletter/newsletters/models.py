# -*- coding: utf-8 -*-

import csv
import sys
import os
import re
from datetime import datetime
from os.path import dirname

import smtplib
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate

from sqlalchemy import (Table, Column, Boolean, BigInteger, Integer, Float,
                        String, Date, DateTime, ForeignKey, DECIMAL, Text)
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from pyramid import threadlocal
import logging
log = logging.getLogger(__name__)

class Newsletter(Base):
    __tablename__ = 'Newsletter'
    id               = Column(BigInteger, primary_key=True)
    subject          = Column(String(255))
    description      = Column(Text())
    type             = Column(String(255))
    status           = Column(String(255))
    sender_address   = Column(String(255))
    sender_name      = Column(String(255))
    subscriber_count = Column(BigInteger)
    start_on         = Column(DateTime)
    created_at       = Column(DateTime)
    updated_at       = Column(DateTime)

    csv_fields = ('email', 'id', 'name')

    def subscriber_file(self):
        fname = 'altair' + str(self.id) + '.csv'
        csv_file = os.path.join(Newsletter.subscriber_dir(), fname)
        return fname if os.path.exists(csv_file) else None

    @staticmethod
    def subscriber_dir():
        return os.path.abspath(dirname(dirname(__file__))) + '/csv'

    @staticmethod
    def add(newsletter):
        newsletter.created_at = datetime.now()
        newsletter.updated_at = datetime.now()
        session.add(newsletter)
        session.flush()
        return newsletter.id

    @staticmethod
    def get(id):
        return session.query(Newsletter).filter(Newsletter.id==id).first()

    @staticmethod
    def update(newsletter):
        newsletter.updated_at = datetime.now()
        session.merge(newsletter)
        session.flush()

    @staticmethod
    def delete(newsletter):
        session.delete(newsletter)

    @staticmethod
    def all():
        return session.query(Newsletter).all()

    @staticmethod
    def get_reservations():
        return session.query(Newsletter).\
               filter(Newsletter.status == 'waiting').\
               filter(Newsletter.start_on < datetime.now())

    @staticmethod
    def save_file(id, file):
        if file:
            csv_dir = Newsletter.subscriber_dir()
            if not os.path.isdir(csv_dir):
                os.mkdir(csv_dir)

            csv_file = csv.DictWriter(open(os.path.join(csv_dir, 'altair' + str(id) + '.csv'), 'w'), Newsletter.csv_fields)
            for row in csv.DictReader(file, Newsletter.csv_fields):
                row['name'] = Newsletter.encode(row['name'])
                if Newsletter.validate_email(row['email']): csv_file.writerow(row)

    @staticmethod
    def encode(string):
        if not string: return string

        encoded_name = ''
        codecs = ['utf-8', 'euc_jp', 'cp932', 'shift_jis']
        for codec in codecs:
            try:
                encoded_name = string.decode(codec).encode('utf-8')
                break
            except:
                continue
        if encoded_name:
            return encoded_name
        else:
            return False

    @staticmethod
    def validate_email(email):
        if email is not None and len(email) > 6:
            if re.match(r'^.+@[^.].*\.[a-z]{2,10}$', email) is not None:
                return True
        return False

    def test_mail(self, recipient=None):
        subject = u'【テスト送信】' + self.subject
        self.send(recipient=recipient, name='テスト', subject=subject)

    def send(self, **options):
        # settings
        if 'settings' in options:
            settings = options['settings']
        else:
            registry = threadlocal.get_current_registry()
            settings = registry.settings

        # sender
        if self.sender_address:
            from_addr = self.sender_address
            if self.sender_name:
                sender_name = str(Header(self.sender_name, 'ISO-2022-JP'))
                sender = u'%s <%s>' % (sender_name, self.sender_address)
            else:
                sender = self.sender_address
        else:
            from_addr = sender = settings['mail.message.sender']

        # recipient
        if 'recipient' in options:
            recipient = options['recipient']
        else:
            recipient = settings['mail.report.recipient']

        # body, html
        options['name'] = unicode(options['name'], 'utf-8')
        description = self.description.replace('${name}', options['name'])
        body = html = None
        if self.type == 'html':
            html = description
        else:
            body = description

        # subject
        if 'subject' in options:
            subject = options['subject']
        else:
            subject = self.subject
        subject = subject.replace('${name}', options['name'])

        mailer = Mailer(settings)
        mailer.create_message(
            sender = sender,
            recipient = recipient,
            subject = subject,
            body = body,
            html = html
        )   
        try:
            mailer.send(from_addr, recipient)
        except:
            return False
        return True


class Mailer(object):
    def __init__(self, settings):
        self.settings = settings

    def create_message(self,
                       sender=None,
                       recipient=None,
                       subject=None,
                       body=None,
                       html=None,
                       encoding=None):

        encoding = self.settings['mail.message.encoding']
        if html:
            mime_type = 'html' 
            mime_text = html
        else:
            mime_type = 'plain'
            mime_text = body

        msg = MIMEText(mime_text.encode(encoding, 'ignore'), mime_type, encoding)
        msg['Subject'] = Header(subject, encoding)
        msg['From'] = sender
        msg['To'] = recipient
        msg['Date'] = formatdate()
        self.message = msg

    def send(self, from_addr, to_addr):
        smtp = smtplib.SMTP(self.settings['mail.host'], self.settings['mail.port'])
        smtp.sendmail(from_addr, [to_addr], self.message.as_string())
        smtp.close()

