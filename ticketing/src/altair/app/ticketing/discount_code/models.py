# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier
from altair.app.ticketing.utils import rand_string
from altair.saannotation import AnnotatedColumn
from pyramid.i18n import TranslationString as _
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Boolean, Integer, DateTime, Unicode, UnicodeText, String
from standardenum import StandardEnum

logger = logging.getLogger(__name__)


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

    @property
    def target(self):
        return self.DiscountCodeTarget

    @property
    def target_count(self):
        return len(self.DiscountCodeTarget)

    @property
    def available_status(self):
        """割引コード設定の適用可能状態を判定、無効時には理由をリストで返す"""
        reasons = []
        if not self.is_valid:
            reasons.append(u'「有効・無効フラグ」にチェックがありません。')

        if self.target_count == 0:
            reasons.append(u'適用対象が設定されていません。')

        if self.issued_by == 'own':
            now = datetime.now()
            if (self.start_at is not None and self.start_at > now) \
                    or (self.end_at is not None and self.end_at < now):
                reasons.append(u'有効期間外です。')

            if len(self.code) == 0:
                reasons.append(u'コードが自社によって生成されていません。')

        return True if not reasons else reasons


class UsedDiscountCodeCart(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'UsedDiscountCodeCart'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCode.id'), nullable=True)
    code = AnnotatedColumn(String(12), _a_label=_(u'割引コード'), nullable=True)
    carted_product_item_id = AnnotatedColumn(Identifier, ForeignKey('CartedProductItem.id'))
    carted_product_item = relationship("CartedProductItem", backref="used_discount_codes")


class UsedDiscountCodeOrder(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'UsedDiscountCodeOrder'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    discount_code_id = AnnotatedColumn(Identifier, ForeignKey('DiscountCode.id'), nullable=True)
    discount_code = relationship('DiscountCodeCode',
                                 backref='UsedDiscountCodeOrder',
                                 cascade='all'
                                 )
    code = AnnotatedColumn(String(12), _a_label=_(u'割引コード'), nullable=True)
    canceled_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'キャンセル日時'))
    refunded_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'払戻日時'))
    ordered_product_item_id = AnnotatedColumn(Identifier, ForeignKey('OrderedProductItem.id'))
    ordered_product_item = relationship("OrderedProductItem", backref="used_discount_codes")
    ordered_product_item_token_id = AnnotatedColumn(Identifier, ForeignKey('OrderedProductItemToken.id'))
    ordered_product_item_token = relationship("OrderedProductItemToken", backref="used_discount_codes")


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
    used_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'使用日時'))

    # コードの生成時に使用できる文字種
    available_letters = 'ACEFGHKLMNPQRTWXY34679'

    @property
    def order(self):
        if len(self.UsedDiscountCodeOrder) == 0:
            return None

        return self.UsedDiscountCodeOrder[0].ordered_product_item.ordered_product.order


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


def insert_specific_number_code(num, first_4_digits, data):
    """
    ユニークなコードを生成し、既存のレコードと重複がないことを確かめてインサート
    """
    try:
        for _ in range(num):
            data = _add_code_str(first_4_digits, data)
            code = DiscountCodeCode(
                discount_code_setting_id=data['discount_code_setting_id'],
                organization_id=data['organization_id'],
                operator_id=data['operator_id'],
                code=data['code'],
            )
            code.add()
    except SQLAlchemyError as e:
        logger.error(
            'Failed to create discount codes. '
            'base_data: {} '
            'error_message: {}'.format(
                str(data),
                str(e.message)
            )
        )
        return False

    return True


def _add_code_str(first_4_digits, data):
    """コードの生成を行う, 既存コードと重複あれば生成をループ"""
    code_str = first_4_digits + rand_string(DiscountCodeCode.available_letters, 8)
    if _if_generating_code_exists(code_str, data['organization_id']):
        data.update({'code': code_str})
        return data
    else:
        logger.info('code: {} already exists for organization_id: {}.'.format(data['code'], data['organization_id']))
        _add_code_str(first_4_digits, data)


def _if_generating_code_exists(code, organization_id):
    """すでに作成済のコードではないか確認する

    :param str code:
    :param int, dict organization_id:
    :return: boolean Trueなら未作成のコード、Falseなら作成済み
    """
    try:
        DiscountCodeCode.query.filter(
            DiscountCodeCode.organization_id == organization_id,
            DiscountCodeCode.code == code,
        ).one()
        return False
    except NoResultFound:
        return True


def delete_discount_code_setting(setting):
    # TODO 削除を禁止する各条件を後々で用意する

    setting.delete()


def delete_all_discount_code(setting_id):
    """既存のコードを全削除する"""
    # TODO 削除を禁止する各条件を後々で用意する
    query = DiscountCodeCode.query.filter_by(discount_code_setting_id=setting_id)
    count = query.count()
    if count > 0:
        codes = query.all()
        for code in codes:
            code.delete()

    return count
