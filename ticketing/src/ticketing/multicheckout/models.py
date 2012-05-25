# -*- coding:utf-8 -*-

""" TBA
"""
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()


class MultiCheckoutRequestCard(Base):
    __tablename__ = 'multicheckout_request_card'
    id = sa.Column(sa.Integer, primary_key=True)

    query = DBSession.query_property()

    #order

    ItemCd = sa.Column(sa.Unicode(3))
    ItemName = sa.Column(sa.Unicode(44)) # 44バイト...
    OrderYMD = sa.Column(sa.Unicode(8)) # YYYYMMDD
    SalesAmount = sa.Column(sa.Integer)
    TaxCarriage = sa.Column(sa.Integer)
    FreeData = sa.Column(sa.Unicode(32)) # 32バイト...
    ClientName = sa.Column(sa.Unicode(40))
    MailAddress = None
    MailSend = None

    # card
    CardNo = None
    CardLimit = None
    CardHolderName = None
    PayKindCd = None
    PayCount = None
    SecureKind = None


    # Secure Code
    Code = None

    # 3DSecure

    Mvn = None
    Xid = None
    Ts = None
    ECI = None
    CAVV = None
    CavvAlgorithm = None
    CardNo = None