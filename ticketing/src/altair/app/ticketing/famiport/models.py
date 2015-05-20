# -*- coding: utf-8 -*-
import sqlalchemy as sa
from altair.app.ticketing.models import (
    Base,
    BaseModel,
    DBSession,
    Identifier,
    WithTimestamp,
    )
from .utils import InformationResultCodeEnum


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


class FamiPortInformationMessage(Base, BaseModel, WithTimestamp):
    __tablename__ = 'FamiPortInformationMessage'
    __table_args__= (sa.UniqueConstraint('result_code'),)

    id = sa.Column(Identifier, primary_key=True)
    result_code = sa.Column(sa.Enum('WithInformation', 'ServiceUnavailable'), unique=True, nullable=False)
    message = sa.Column(sa.Unicode(length=1000), nullable=True)

    @classmethod
    def create(cls, result_code, message):
        return cls(result_code=result_code, message=message)

    @classmethod
    def get_message(cls, information_result_code, default_message=None):
        if not isinstance(information_result_code, InformationResultCodeEnum):
            return None
        query = FamiPortInformationMessage.filter_by(result_code=information_result_code.name)
        famiport_information_message = query.first()
        if famiport_information_message:
            return famiport_information_message.message
        else:
            return default_message