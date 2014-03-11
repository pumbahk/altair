# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from datetime import datetime
import uuid
import sqlalchemy as sa
import sqlalchemy.orm as orm
from altair.app.ticketing.models import Identifier
from sqlalchemy.sql import functions as sqlf
# from altair.app.ticketing.core import models as c_models
# from altair.app.ticketing.core import api as c_api
from sqlalchemy.types import Boolean, BigInteger, Integer, Float, String, Date, DateTime, Numeric, Unicode, UnicodeText, TIMESTAMP, Time
from altair.app.ticketing.models import DBSession, Base
from altair.saannotation import AnnotatedColumn

class CheckinIdentity(Base):
    __tablename__ = 'CheckinIdentity'

    query = DBSession.query_property()

    id = sa.Column(Identifier, primary_key=True)
    operator_id = sa.Column(Identifier,  sa.ForeignKey("Operator.id"),  index=True,  nullable=False)
    device_id = AnnotatedColumn(String(64), _a_label=(u"チェックインステーションの筐体のid"), nullable=False, index=True)
    login_at = AnnotatedColumn(TIMESTAMP, 
                               server_default=sqlf.current_timestamp(), 
                               default=datetime.now,
                               _a_label=(u"ログイン時刻"))
    logout_at = AnnotatedColumn(TIMESTAMP, _a_label=(u"ログアウト時刻"))
    secret = sa.Column(String(32), nullable=False) #conflict?
    deleted_at = sa.Column(TIMESTAMP, nullable=True)

    operator = orm.relationship("Operator")

    def logout(self):
        self.logout_at = datetime.now()

    def login(self):
        self.login_at = datetime.now()
        self.secret=uuid.uuid4().hex
