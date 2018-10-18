# -*- coding:utf-8 -*-

from altair.app.ticketing.models import (
    Base, Identifier, BaseModel,
    WithTimestamp, LogicallyDeleted
)
from altair.saannotation import AnnotatedColumn
from pyramid.i18n import TranslationString as _
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import UnicodeText, Integer


class NotifyUpdateTicketInfoTask(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "NotifyUpdateTicketInfoTask"
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    ticket_bundle_id = AnnotatedColumn(Identifier, ForeignKey('TicketBundle.id'), nullable=False,
                                       _a_label=_(u'チケット券面構成ID'))
    ticket_bundle = relationship('TicketBundle', backref='NotifyUpdateTicketInfoTask')
    operator_id = AnnotatedColumn(Identifier, ForeignKey('Operator.id'), nullable=False, _a_label=_(u'オペレーターID'))
    operator = relationship('Operator', backref='NotifyUpdateTicketInfoTask')
    status = AnnotatedColumn(Integer(), nullable=False, _a_label=_(u'ステータス'))
    errors = AnnotatedColumn(UnicodeText(), nullable=True, _a_label=_(u'エラー内容'), server_default='')
