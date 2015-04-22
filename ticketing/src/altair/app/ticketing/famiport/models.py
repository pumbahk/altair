# -*- coding: utf-8 -*-
import sqlalchemy as sa
from altair.app.ticketing.models import (
    Base,
    BaseModel,
    DBSession,
    Identifier,
    WithTimestamp,
    )


class FamiPortOrderNoSequence(Base, BaseModel, WithTimestamp):
    __tablename__ = 'FamiPortOrderNoSequence'

    id = sa.Column(Identifier, primary_key=True)

    @classmethod
    def get_next_value(cls, name):
        seq = cls()
        DBSession.add(seq)
        DBSession.flush()
        return seq.id


class FamiPortOrder(Base, BaseModel, WithTimestamp):
    __tablename__ = 'FamiPortOrder'

    id = sa.Column(Identifier, primary_key=True)
    order_no = sa.Column(sa.String(255), nullable=False)
    barcode_no = sa.Column(sa.String(255), nullable=False)
