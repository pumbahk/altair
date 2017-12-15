# encoding: utf-8

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier
from altair.saannotation import AnnotatedColumn
from pyramid.i18n import TranslationString as _
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Boolean, Integer, DateTime, Unicode, UnicodeText, String
from standardenum import StandardEnum


class CodeOrganizerEnum(StandardEnum):
    sports_service = ('sports_service', u'スポーツサービス開発')
    own = ('own', u'自社')


class DiscountCodeSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DiscountCodeSetting'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    first_digit = AnnotatedColumn(Unicode(1), nullable=True, _a_label=_(u'コード1桁め'))
    following_2to4_digits = AnnotatedColumn(Unicode(3), nullable=True, _a_label=_(u'コード2〜4桁め'))
    first_4_digits = column_property(first_digit + following_2to4_digits)
    name = AnnotatedColumn(Unicode(255), nullable=False, _a_label=_(u'コード名称'))
    issued_by = AnnotatedColumn(Unicode(255), nullable=False, _a_label=_(u'コード管理元'))
    criterion = AnnotatedColumn(Unicode(255), nullable=False, _a_label=_(u'適用基準'))
    condition_price_amount = AnnotatedColumn(Unicode(255), nullable=True, _a_label=_(u'条件数値（チケット価格）'))
    condition_price_more_or_less = AnnotatedColumn(Unicode(255), nullable=True, _a_label=_(u'判定方法'))
    benefit_amount = AnnotatedColumn(Integer(8), nullable=False, _a_label=_(u'割引内容：数値'))
    benefit_unit = AnnotatedColumn(Unicode(1), nullable=False, _a_label=_(u'割引内容：単位'))
    organization_id = AnnotatedColumn(Identifier, ForeignKey('Organization.id'), nullable=False, _a_label=_(u'組織ID'))
    organization = relationship('Organization',
                                backref='DiscountCodeSetting',
                                cascade='all'
                                )
    is_valid = AnnotatedColumn(Boolean, nullable=False, _a_label=_(u'有効・無効フラグ'))
    start_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'適用開始日時'))
    end_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'適用終了日時'))
    explanation = AnnotatedColumn(UnicodeText, nullable=True, _a_label=_(u'割引概要説明文 '))

    code = relationship('DiscountCodeCode', backref='DiscountCodeSetting')


class UsedDiscountCodeCart(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'UsedDiscountCodeCart'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCode.id'), nullable=True)
    code = AnnotatedColumn(String(12), _a_label=_(u'ディスカウントコード'), nullable=True)
    carted_product_item_id = AnnotatedColumn(Identifier, ForeignKey('CartedProductItem.id'))
    carted_product_item = relationship("CartedProductItem", backref="used_discount_codes")


class UsedDiscountCodeOrder(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'UsedDiscountCodeOrder'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCode.id'), nullable=True)
    code = AnnotatedColumn(String(12), _a_label=_(u'ディスカウントコード'), nullable=True)
    ordered_product_item_id = AnnotatedColumn(Identifier, ForeignKey('OrderedProductItem.id'))
    ordered_product_item = relationship("OrderedProductItem", backref="used_discount_codes")


class DiscountCodeCode(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DiscountCode'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_setting_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCodeSetting.id'), nullable=False,
                                               _a_label=_(u'割引コード設定ID'))
    discount_code_setting = relationship('DiscountCodeSetting',
                                         backref='DiscountCode',
                                         cascade='all'
                                         )
    organization_id = AnnotatedColumn(Identifier, ForeignKey('Organization.id'), nullable=False, _a_label=_(u'組織ID'))
    organization = relationship('Organization',
                                backref='DiscountCode',
                                cascade='all'
                                )
    operator_id = AnnotatedColumn(Identifier, ForeignKey('Operator.id'), nullable=False, _a_label=_(u'オペレーターID'))
    operator = relationship('Operator',
                            backref='Operator',
                            cascade='all'
                            )
    code = AnnotatedColumn(Unicode(12), nullable=True, _a_label=_(u'クーポン・割引コード'))
    order_no = AnnotatedColumn(Unicode(255), nullable=True, _a_label=_(u'予約番号'))
    used_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'利用日時'))


class DiscountCodeTarget(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DiscountCodeTarget'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_setting_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCodeSetting.id'), nullable=False,
                                               _a_label=_(u'割引コード設定ID'))
    discount_code_setting = relationship('DiscountCodeSetting',
                                         backref='DiscountCodeTarget',
                                         cascade='all'
                                         )
    event_id = AnnotatedColumn(Identifier, ForeignKey('Event.id'), nullable=False, _a_label=_(u'イベントID'))
    event = relationship('Event',
                         backref='DiscountCodeTarget',
                         cascade='all'
                         )
    performance_id = AnnotatedColumn(Identifier, ForeignKey('Performance.id'), nullable=False, _a_label=_(u'パフォーマンスID'))
    performance = relationship('Performance',
                               backref='DiscountCodeTarget',
                               cascade='all'
                               )


def delete_discount_code_setting(setting):
    # TODO 削除を禁止する各条件を後々で用意する

    setting.delete()
