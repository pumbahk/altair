# encoding: utf-8

import sqlalchemy as sa
from altair.models import Identifier
from ..models import Base, FamiPortRefund, FamiPortRefundEntry, FamiPortTicket, FamiPortShop

class FamiPortOperator(Base):
    __tablename__ = 'FamiPortOperator'

    id = sa.Column(Identifier, primary_key=True, nullable=False, autoincrement=True)
    user_name = sa.Column(sa.Unicode(32), nullable=False, unique=True)
    password = sa.Column(sa.Unicode(96), nullable=False)
    role = sa.Column(sa.Unicode(32), nullable=False)

    @property
    def has_perm_for_personal_info(self):
        if self.role not in ('administrator', 'superuser',):
            return False
        return True