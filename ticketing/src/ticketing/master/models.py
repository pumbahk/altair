from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

'''
 Master Data
'''
class Prefecture(Base):
    __tablename__ = 'Prefecture'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    @staticmethod
    def all():
        return session.query(Prefecture).all()

    @staticmethod
    def get(prefecture_id):
        return session.query(Prefecture).filter(Prefecture.id == prefecture_id).first()


class Bank(Base):
    __tablename__ = 'Bank'
    id = Column(BigInteger, primary_key=True)
    code = Column(BigInteger)
    name = Column(String(255))

class BankAccount(Base):
    __tablename__ = 'BankAccount'
    id = Column(BigInteger, primary_key=True)
    back_id = Column(BigInteger, ForeignKey("Bank.id"))
    bank = relationship("Bank", backref=backref('addresses', order_by=id))
    account_type = Column(Integer)
    account_number = Column(String(255))
    account_owner = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)



