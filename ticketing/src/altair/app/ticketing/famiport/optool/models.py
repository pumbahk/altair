# encoding: utf-8

import sqlalchemy as sa
from altair.models import Identifier
from ..models import Base, FamiPortRefund, FamiPortRefundEntry, FamiPortTicket, FamiPortShop
from datetime import datetime, timedelta

class FamiPortOperator(Base):
    __tablename__ = 'FamiPortOperator'

    time_now = datetime.now()
    expired_time = time_now + timedelta(days=180)

    id = sa.Column(Identifier, primary_key=True, nullable=False, autoincrement=True)
    user_name = sa.Column(sa.Unicode(32), nullable=False, unique=True)
    password = sa.Column(sa.Unicode(96), nullable=False)
    role = sa.Column(sa.Unicode(32), nullable=False)
    email = sa.Column(sa.Unicode(120), nullable=False, unique=True)
    created_at = sa.Column(sa.DateTime, default=time_now, nullable=False)
    updated_at = sa.Column(sa.DateTime, default=time_now, onupdate=time_now, nullable=False)
    expired_at = sa.Column(sa.DateTime, default=expired_time, onupdate=expired_time, nullable=True)
    active = sa.Column(sa.Boolean)

    @property
    def has_perm_for_personal_info(self):
        if self.role not in ('administrator', 'superuser',):
            return False
        return True