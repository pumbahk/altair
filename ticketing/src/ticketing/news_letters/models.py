from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from pprint import pprint
import logging
import os
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
        if subscriber_file:
            count = 0
            for line in subscriber_file.readlines(): count += 1
            log.debug(count)

            open(os.path.join('/tmp', 'altair' + str(id) + '.csv'), 'w').write(subscriber_file.read())

            news_letter = NewsLetter.get(id)
            news_letter.subscriber_count = count
            NewsLetter.update(news_letter)
