from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

import csv
import sys
import os
import re
from os.path import dirname
import logging
log = logging.getLogger(__name__)

'''

 NewsLetter

'''
class NewsLetter(Base):
    __tablename__ = 'NewsLetter'
    id = Column(BigInteger, primary_key=True)
    subject = Column(String(255))
    description = Column(String(5000))
    start_on = Column(DateTime)
    subscriber_count = Column(BigInteger)
    status = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)

    def subscriber_file(self):
        return '/tmp/altair' + str(self.id) + '.csv'

    @staticmethod
    def add(news_letter):
        log.debug(vars(news_letter))
        session.add(news_letter)

    @staticmethod
    def get(id):
        return session.query(NewsLetter).filter(NewsLetter.id==id).first()

    @staticmethod
    def update(news_letter):
        session.merge(news_letter)
        session.flush()

    @staticmethod
    def all():
        return session.query(NewsLetter).all()

    @staticmethod
    def save_file(id, form):
        subscriber_file = form.subscriber_file.data.file
        log.debug(subscriber_file)
        if subscriber_file:
            csv_dir = os.path.abspath(dirname(dirname(__file__))) + '/csv'
            log.debug(csv_dir)
            if not os.path.isdir(csv_dir):
                os.mkdir(csv_dir)

            fields = ['id', 'name', 'email']
            csv_file = csv.DictWriter(open(os.path.join(csv_dir, 'altair' + str(id) + '.csv'), 'w'), fields)
            count = 0
            for row in csv.DictReader(subscriber_file, fields):
                if NewsLetter.validateEmail(row['email']):
                    csv_file.writerow(row)
                    count += 1

            news_letter = NewsLetter.get(id)
            news_letter.subscriber_count = count
            NewsLetter.update(news_letter)

    @staticmethod
    def validateEmail(email):
        log.debug(email)
        if email is not None and len(email) > 6:
            if re.match('[\w\.-]+@[\w\.-]+\.\w{2,4}', email) != None:
                return True
        return False

