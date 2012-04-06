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

 Newsletter

'''
class Newsletter(Base):
    __tablename__ = 'Newsletter'
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
    def add(newsletter):
        log.debug(vars(newsletter))
        session.add(newsletter)

    @staticmethod
    def get(id):
        return session.query(Newsletter).filter(Newsletter.id==id).first()

    @staticmethod
    def update(newsletter):
        session.merge(newsletter)
        session.flush()

    @staticmethod
    def all():
        return session.query(Newsletter).all()

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
                if Newsletter.validateEmail(row['email']):
                    csv_file.writerow(row)
                    count += 1

            newsletter = Newsletter.get(id)
            newsletter.subscriber_count = count
            Newsletter.update(newsletter)

    @staticmethod
    def validateEmail(email):
        log.debug(email)
        if email is not None and len(email) > 6:
            if re.match(r'^.+@[^.].*\.[a-z]{2,10}$', email) != None:
                return True
        return False

