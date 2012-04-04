from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

'''

 NewsLetter

'''
class NewsLetter(Base):
    __tablename__ = 'NewsLetter'
    id = Column(BigInteger, primary_key=True)
    subject = Column(String(255))
    description = Column(String(5000))
    start_on = Column(DateTime)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)

    @staticmethod
    def add(news_letter):
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

