# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
from altair.saannotation import AnnotatedColumn
from pyramid.i18n import TranslationString as _
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Boolean, Integer, DateTime, Unicode, UnicodeText, String
from standardenum import StandardEnum

logger = logging.getLogger(__name__)


class CodeOrganizerEnum(StandardEnum):
    sports_service = ('sports_service', u'スポーツサービス開発')
    own = ('own', u'自社')


class BenefitUnitEnum(StandardEnum):
    percent = ('%', u'%')
    yen = ('y', u'円')


class ConditionPriceMoreOrLessEnum(StandardEnum):
    less = ('less', u'以下')


class DiscountCodeSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    クーポン・割引コード機能の核となるモデルクラス
    割引の開始時期や終了時期、割引内容の詳細設定を管理
    """
    __tablename__ = 'DiscountCodeSetting'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    first_digit = AnnotatedColumn(Unicode(1), nullable=True, _a_label=_(u'コード1桁め'))
    following_2to4_digits = AnnotatedColumn(Unicode(3), nullable=True, _a_label=_(u'コード2〜4桁め'))
    name = AnnotatedColumn(Unicode(255), nullable=False, _a_label=_(u'コード名称'))
    issued_by = AnnotatedColumn(Unicode(255), nullable=False, _a_label=_(u'コード管理元'))
    criterion = AnnotatedColumn(Unicode(255), nullable=False, _a_label=_(u'適用基準'))
    condition_price_amount = AnnotatedColumn(Unicode(255), nullable=True, _a_label=_(u'適用基準: 条件数値'))
    condition_price_more_or_less = AnnotatedColumn(Unicode(255), nullable=True, _a_label=_(u'適用基準: 判定方法'))
    benefit_amount = AnnotatedColumn(Integer(8), nullable=False, _a_label=_(u'割引内容：数値'))
    benefit_unit = AnnotatedColumn(Unicode(1), nullable=False, _a_label=_(u'割引内容：単位'))
    organization_id = AnnotatedColumn(Identifier, ForeignKey('Organization.id'), nullable=False, _a_label=_(u'組織ID'))
    organization = relationship('Organization', backref='dc_settings')
    is_valid = AnnotatedColumn(Boolean, nullable=False, _a_label=_(u'有効・無効フラグ'))
    start_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'適用開始日時'))
    end_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'適用終了日時'))
    explanation = AnnotatedColumn(UnicodeText, nullable=True, _a_label=_(u'割引概要説明文 '))

    @property
    def first_4_digits(self):
        return self.first_digit + self.following_2to4_digits

    @property
    def target(self):
        return self.DiscountCodeTarget

    @property
    def target_count(self):
        return DiscountCodeTarget.filter_by(discount_code_setting_id=self.id).count()

    @property
    def target_stock_type_count(self):
        return DiscountCodeTargetStockType.filter_by(discount_code_setting_id=self.id).count()

    @property
    def code_count(self):
        return DiscountCodeCode.filter_by(discount_code_setting_id=self.id).count()

    @property
    def available_status(self):
        """割引コード設定の適用可能状態を判定、無効時には理由をリストで返す"""
        reasons = []
        if not self.is_valid:
            reasons.append(u'「有効・無効フラグ」にチェックがありません。')

        if self.target_count == 0 and self.target_stock_type_count == 0:
            reasons.append(u'適用公演と適用席種のどちらにも設定がありません。')

        if self.issued_by == 'own':
            now = datetime.now()
            if (self.start_at is not None and self.start_at > now) \
                    or (self.end_at is not None and self.end_at < now):
                reasons.append(u'有効期間外です。')

            if self.code_count == 0:
                reasons.append(u'コードが自社によって生成されていません。')

        return True if not reasons else reasons

    @staticmethod
    def is_valid_checked(setting_id, session=None):
        """
        設定の有効フラグがONになっているかチェックする
        :param setting_id: 割引コード設定ID
        :param session: オプション。slaveの使用を前提
        :return: Boolean
        """
        q = session.query(DiscountCodeSetting) if session else DBSession.query(DiscountCodeSetting)
        setting = q.filter_by(id=setting_id).one()
        return setting.is_valid


class UsedDiscountCodeCart(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    `Cart`に紐づく使用されたコードと、その割引適用金額の管理
    """
    __tablename__ = 'UsedDiscountCodeCart'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCode.id'), nullable=True)
    code = AnnotatedColumn(String(12), _a_label=_(u'割引コード'), nullable=True)
    carted_product_item_id = AnnotatedColumn(Identifier, ForeignKey('CartedProductItem.id'))
    carted_product_item = relationship("CartedProductItem", backref="used_discount_codes")
    finished_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'カート処理日時'))
    discount_code_setting_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCodeSetting.id'), nullable=False,
                                               _a_label=_(u'割引コード設定ID'))
    discount_code_setting = relationship('DiscountCodeSetting', backref='used_discount_code_carts')
    applied_amount = AnnotatedColumn(Integer(8), nullable=False, _a_label=_(u'割引の発生金額'))
    benefit_amount = AnnotatedColumn(Integer(8), nullable=False, _a_label=_(u'割引内容：数値'))
    benefit_unit = AnnotatedColumn(Unicode(1), nullable=False, _a_label=_(u'割引内容：単位'))


class UsedDiscountCodeOrder(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    `Order`に紐づく使用されたコードと、その割引適用金額の管理
    """
    __tablename__ = 'UsedDiscountCodeOrder'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCode.id'), nullable=True)
    discount_code = relationship('DiscountCodeCode', backref='used_discount_code_orders')
    code = AnnotatedColumn(String(12), _a_label=_(u'割引コード'), nullable=True)
    canceled_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'キャンセル日時'))
    refunded_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'払戻日時'))
    ordered_product_item_id = AnnotatedColumn(Identifier, ForeignKey('OrderedProductItem.id'))
    ordered_product_item = relationship("OrderedProductItem", backref="used_discount_codes")
    ordered_product_item_token_id = AnnotatedColumn(Identifier, ForeignKey('OrderedProductItemToken.id'))
    ordered_product_item_token = relationship("OrderedProductItemToken", backref="used_discount_codes")
    discount_code_setting_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCodeSetting.id'), nullable=False, _a_label=_(u'割引コード設定ID'))
    discount_code_setting = relationship('DiscountCodeSetting', backref='used_discount_code_orders')
    applied_amount = AnnotatedColumn(Integer(8), nullable=False, _a_label=_(u'割引の発生金額'))
    benefit_amount = AnnotatedColumn(Integer(8), nullable=False, _a_label=_(u'割引内容：数値'))
    benefit_unit = AnnotatedColumn(Unicode(1), nullable=False, _a_label=_(u'割引内容：単位'))

    @staticmethod
    def count_exists_valid_order(first_4_digits, session=None):
        """
        コードの使用履歴から有効な予約に紐付いているコードの件数を取得する
        :param first_4_digits: 割引コード設定のコードの頭4桁
        :param session: オプション。slaveの使用を前提
        :return: 予約に紐付いているコードの件数
        """
        from altair.app.ticketing.orders.models import Order, OrderedProductItem, OrderedProduct
        q = session.query(UsedDiscountCodeOrder) if session else DBSession.query(UsedDiscountCodeOrder)
        valid_order_cnt = q.join(
            OrderedProductItem,
            OrderedProduct,
            Order
        ).filter(
            UsedDiscountCodeOrder.code.like(first_4_digits + "%"),
            UsedDiscountCodeOrder.canceled_at.is_(None),
            UsedDiscountCodeOrder.refunded_at.is_(None),
            Order.canceled_at.is_(None),
            Order.refunded_at.is_(None)
        ).count()

        return valid_order_cnt


class DiscountCodeCode(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    コード管理元が自社の場合に利用できる自社コードの管理
    """
    __tablename__ = 'DiscountCode'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_setting_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCodeSetting.id'), nullable=False, _a_label=_(u'割引コード設定ID'))
    discount_code_setting = relationship('DiscountCodeSetting', backref='dc_codes')
    organization_id = AnnotatedColumn(Identifier, ForeignKey('Organization.id'), nullable=False, _a_label=_(u'組織ID'))
    organization = relationship('Organization', backref='dc_codes')
    operator_id = AnnotatedColumn(Identifier, ForeignKey('Operator.id'), nullable=False, _a_label=_(u'オペレーターID'))
    operator = relationship('Operator', backref='dc_codes')
    code = AnnotatedColumn(Unicode(12), nullable=True, _a_label=_(u'クーポン・割引コード'))
    used_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'使用日時'))

    # コードの生成時に使用できる文字種
    AVAILABLE_LETTERS = 'ACEFGHKLMNPQRTWXY34679'

    @property
    def order(self):
        order = None
        if len(self.used_discount_code_orders) == 0:
            return order

        desc_ordered = sorted(self.used_discount_code_orders, key=lambda x: x.created_at, reverse=True)
        latest = desc_ordered[0]
        if latest.ordered_product_item and \
                latest.ordered_product_item.ordered_product and \
                latest.ordered_product_item.ordered_product.order:
            order = latest.ordered_product_item.ordered_product.order

        return order


class DiscountCodeTarget(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    割引コードの対象となるパフォーマンスを管理する
    """
    __tablename__ = 'DiscountCodeTarget'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_setting_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCodeSetting.id'), nullable=False, _a_label=_(u'割引コード設定ID'))
    discount_code_setting = relationship('DiscountCodeSetting', backref='dc_targets')
    event_id = AnnotatedColumn(Identifier, ForeignKey('Event.id'), nullable=False, _a_label=_(u'イベントID'))
    event = relationship('Event', backref='dc_targets')
    performance_id = AnnotatedColumn(Identifier, ForeignKey('Performance.id'), nullable=False, _a_label=_(u'パフォーマンスID'))
    performance = relationship('Performance', backref='dc_targets')


class DiscountCodeTargetStockType(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    割引コードの対象となる販売区分と席種を管理する
    """
    __tablename__ = 'DiscountCodeTargetStockType'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_setting_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCodeSetting.id'), nullable=False,
                                               _a_label=_(u'割引コード設定ID'))
    discount_code_setting = relationship('DiscountCodeSetting', backref='dc_target_stock_types')
    event_id = AnnotatedColumn(Identifier, ForeignKey('Event.id'), nullable=False, _a_label=_(u'イベントID'))
    event = relationship('Event', backref='dc_target_stock_types')
    performance_id = AnnotatedColumn(Identifier, ForeignKey('Performance.id'), nullable=False, _a_label=_(u'パフォーマンスID'))
    performance = relationship('Performance', backref='dc_target_stock_types')
    stock_type_id = AnnotatedColumn(Identifier, ForeignKey('StockType.id'), nullable=False, _a_label=_(u'席種ID'))
    stock_type = relationship('StockType', backref='dc_target_stock_types')
