# -*- coding: utf-8 -*-

import logging

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier
from altair.saannotation import AnnotatedColumn
from pyramid.i18n import TranslationString as _
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Boolean, Integer, DateTime, Unicode

logger = logging.getLogger(__name__)


class Passport(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Passport'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    name = AnnotatedColumn(Unicode(255), nullable=False, _a_label=_(u'パスポート名称'))
    available_day = AnnotatedColumn(Integer(255), nullable=False, _a_label=_(u'有効日数'))
    daily_passport = AnnotatedColumn(Boolean, nullable=True, _a_label=_(u'平日パスポート'))
    is_valid = AnnotatedColumn(Boolean, nullable=True, _a_label=_(u'有効・無効フラグ'))
    organization_id = AnnotatedColumn(Identifier, ForeignKey('Organization.id'), nullable=False, _a_label=_(u'組織ID'))
    performance_id = AnnotatedColumn(Identifier, ForeignKey('Performance.id'), nullable=False, _a_label=_(u'パフォーマンス'))
    organization = relationship('Organization',
                                backref='passport',
                                cascade='all'
                                )
    performance = relationship('Performance',
                               backref='passport',
                               cascade='all'
                               )


class PassportNotAvailableTerm(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PassportNotAvailableTerm'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    start_on = AnnotatedColumn(DateTime, _a_label=_(u"開始"))
    end_on = AnnotatedColumn(DateTime, _a_label=_(u"終了"))
    passport = relationship("Passport",
                            backref=orm.backref("terms", uselist=True, cascade="all,delete-orphan")
                            )
    passport_id = AnnotatedColumn(Identifier, ForeignKey('Passport.id'), nullable=False)


class PassportUser(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PassportUser'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    order_attribute_num = AnnotatedColumn(Integer(255), nullable=False, _a_label=_(u'購入情報属性で何人目かのインデックス'))
    expired_at = AnnotatedColumn(DateTime, _a_label=_(u"パスポート有効期限"))
    image_path = AnnotatedColumn(Unicode(1024), nullable=False, _a_label=_(u'顔写真パス'))
    is_valid = AnnotatedColumn(Boolean, nullable=True, _a_label=_(u'有効・無効フラグ'))
    admission_time = AnnotatedColumn(DateTime, _a_label=_(u"最終入場時刻"))
    confirmed_at = AnnotatedColumn(DateTime, _a_label=_(u"本人確認画像確定時間"))
    ordered_product = relationship("OrderedProduct", backref='users')
    ordered_product_id = AnnotatedColumn(Identifier, ForeignKey('OrderedProduct.id'), nullable=False)
    order = relationship("Order", backref='users')
    order_id = AnnotatedColumn(Identifier, ForeignKey('Order.id'), nullable=False)
    passport = relationship("Passport", backref='users')
    passport_id = AnnotatedColumn(Identifier, ForeignKey('Passport.id', ondelete='CASCADE'), nullable=False)


class PassportUserInfo(object):
    def __init__(self, passport_user, passport_kind, last_name, first_name, last_name_kana, first_name_kana, birthday,
                 sex):
        self._passport_user = passport_user
        self._passport_kind = passport_kind
        self._last_name = last_name
        self._first_name = first_name
        self._last_name_kana = last_name_kana
        self._first_name_kana = first_name_kana
        self._birthdaty = birthday
        self._sex = sex

    @property
    def passport_user(self):
        return self._passport_user
