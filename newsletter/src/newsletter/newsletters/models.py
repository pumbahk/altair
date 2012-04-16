# -*- coding: utf-8 -*-

import csv
import sys
import os
import re
from datetime import datetime
from os.path import dirname

from sqlalchemy import (Table, Column, Boolean, BigInteger, Integer, Float,
                        String, Date, DateTime, ForeignKey, DECIMAL, Text)
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from pyramid import threadlocal
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message

from newsletter.utils import StandardEnum

import logging
log = logging.getLogger(__name__)

'''
Newsletter
'''
class Newsletter(Base):
    __tablename__ = 'Newsletter'
    #__table_args__ = {'extend_existing': True}
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

            fields = ['id', 'name', 'email']
            csv_file = csv.DictWriter(open(os.path.join(csv_dir, 'altair' + str(id) + '.csv'), 'w'), fields)
            for row in csv.DictReader(file, fields):
                if Newsletter.validate_email(row['email']): csv_file.writerow(row)

    @staticmethod
    def validate_email(email):
        if email is not None and len(email) > 6:
            if re.match(r'^.+@[^.].*\.[a-z]{2,10}$', email) is not None:
                return True
        return False

    @staticmethod
    def test_mail(id, recipient=None):
        newsletter = Newsletter.get(id)

        registry = threadlocal.get_current_registry()
        settings = registry.settings
        mailer = Mailer.from_settings(settings)

        recipient = recipient if recipient else settings['mail.report.recipients']
        sender = newsletter.sender_address if newsletter.sender_address else settings['mail.message.sender']
        body = html = None
        if newsletter.type == 'html':
            html = newsletter.description.replace('${name}', u'テスト')
        else:
            body = newsletter.description.replace('${name}', u'テスト')

        message = Message(
            sender = sender,
            subject = u'【テスト送信】' + newsletter.subject,
            recipients = [recipient],
            body = body,
            html = html,
        )
        print vars(message)
        mailer.send_immediately(message)

