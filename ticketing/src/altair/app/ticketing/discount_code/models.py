# encoding: utf-8

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier
from altair.saannotation import AnnotatedColumn
from pyramid.i18n import TranslationString as _
from sqlalchemy.orm import column_property
from sqlalchemy.orm import relationship, configure_mappers
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Boolean, Integer, DateTime, Unicode, UnicodeText
from standardenum import StandardEnum


class CodeOrganaizerEnum(StandardEnum):
    sports_service = ('sports_service', u'スポーツサービス開発')
    own = ('own', u'自社')

class DiscountCodeSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DiscountCodeSetting'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    first_digit = AnnotatedColumn(Unicode(1), nullable = True, _a_label=_(u'コード1桁め'))
    following_2to4_digits = AnnotatedColumn(Unicode(3), nullable = True, _a_label=_(u'コード2〜4桁め'))
    first_4_digits = column_property(first_digit + following_2to4_digits)
    name = AnnotatedColumn(Unicode(255), nullable = False, _a_label=_(u'コード名称'))
    issued_by = AnnotatedColumn(Unicode(255), nullable = False, _a_label=_(u'コード管理元'))
    criterion = AnnotatedColumn(Unicode(255), nullable = False, _a_label=_(u'適用基準'))
    condition_price_amount = AnnotatedColumn(Unicode(255), nullable = True, _a_label=_(u'条件数値（チケット価格）'))
    condition_price_more_or_less = AnnotatedColumn(Unicode(255), nullable = True, _a_label=_(u'条件単位（チケット価格）'))
    benefit_amount = AnnotatedColumn(Integer(8), nullable = False, _a_label=_(u'割引内容：数値'))
    benefit_unit = AnnotatedColumn(Unicode(1), nullable = False, _a_label=_(u'割引内容：単位'))
    organization_id = AnnotatedColumn(Identifier, ForeignKey('Organization.id'), nullable=False)
    organization = relationship('Organization',
        backref='discount_code_settings',
        cascade='all'
        )
    is_valid = AnnotatedColumn(Boolean, nullable=False, _a_label=_(u'有効・無効フラグ'))
    start_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'適用開始日時'))
    end_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'適用終了日時'))
    explanation = AnnotatedColumn(UnicodeText, nullable=True, _a_label=_(u'割引概要説明文 '))

configure_mappers()


def delete_discount_code_setting(setting):
    # TODO 削除を禁止する各条件を後々で用意する

    setting.delete()
