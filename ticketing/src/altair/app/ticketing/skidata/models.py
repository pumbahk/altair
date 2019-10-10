# -*- coding: utf-8 -*-

import sqlalchemy as sa
from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
import altair.app.ticketing.skidata.utils as utils
from standardenum import StandardEnum


class SkidataBarcode(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SkidataBarcode'
    id = sa.Column(Identifier, primary_key=True)
    seat_id = sa.Column(Identifier, sa.ForeignKey('Seat.id'), nullable=True)
    seat = sa.orm.relationship('Seat')
    ordered_product_item_token_id = sa.Column(Identifier, sa.ForeignKey('OrderedProductItemToken.id'), nullable=True)
    ordered_product_item_token = sa.orm.relationship('OrderedProductItemToken')
    data = sa.Column(sa.String(30), nullable=False)
    error_code = sa.Column(sa.String(10), nullable=True)
    sent_at = sa.Column(sa.DateTime(), nullable=True)
    canceled_at = sa.Column(sa.DateTime(), nullable=True)

    @staticmethod
    def insert_new_barcode_by_token(ordered_product_item_token, session=DBSession):
        """
        SkidataBarcodeに新規にデータをインサートする。
        引き渡されたOrderedProductItemTokenを元にデータを生成する。
        :param ordered_product_item_token: OrderedProductItemToken
        :param session: DBセッション。デフォルトはマスタ。
        """
        new_barcode = SkidataBarcode()
        new_barcode.seat_id = ordered_product_item_token.seat_id
        new_barcode.ordered_product_item_token_id = ordered_product_item_token.id
        new_barcode.data = utils.issue_new_qr_str()
        session.add(new_barcode)
        _flushing(session)

    @staticmethod
    def is_barcode_exist(barcode):
        """
        指定されたバーコードがSkidataBarcodeに存在するか判定する
        :param barcode: バーコード
        :return: True:存在する, False:存在しない
        """
        return DBSession.query(SkidataBarcode).filter(SkidataBarcode.data == barcode).count() > 0

    @staticmethod
    def find_by_id(barcode_id, session=DBSession):
        """
        指定されたidを元にSkidataBarcodeを取得する
        :param barcode_id: 主キー
        :param session: DBセッション。デフォルトはマスタ。
        :return: SkidataBarcodeデータ
        """
        return session.query(SkidataBarcode).filter(SkidataBarcode.id == barcode_id).first()

    @staticmethod
    def find_all_by_order_no(order_no, session=DBSession):
        """
        指定された予約番号を元に全てのSkidataBarcodeデータを取得する。
        このときキャンセルすみのSkidataBarcodeは除外される。
        :param order_no: 予約番号
        :param session: DBセッション。デフォルトはマスタ。
        :return: SkidataBarcodeデータのリスト
        """
        from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, \
            OrderedProductItemToken
        return session.query(SkidataBarcode) \
            .join(OrderedProductItemToken) \
            .join(OrderedProductItem) \
            .join(OrderedProduct) \
            .join(Order) \
            .filter(Order.order_no == order_no) \
            .filter(SkidataBarcode.canceled_at.is_(None)) \
            .all()


class SkidataPropertyTypeEnum(StandardEnum):
    SalesSegmentGroup = 0
    ProductItem = 1


class SkidataProperty(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SkidataProperty'
    id = sa.Column(Identifier, primary_key=True)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'), nullable=False)
    organization = sa.orm.relationship('Organization')
    prop_type = sa.Column(sa.SmallInteger(), nullable=False)
    name = sa.Column(sa.String(30), nullable=False)
    value = sa.Column(sa.SmallInteger(), nullable=False)


class SkidataPropertyEntry(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SkidataPropertyEntry'
    id = sa.Column(Identifier, primary_key=True)
    skidata_property_id = sa.Column(Identifier, sa.ForeignKey('SkidataProperty.id'), nullable=False)
    property = sa.orm.relationship('SkidataProperty')
    related_id = sa.Column(Identifier, nullable=False)


def _flushing(session):
    try:
        session.flush()
    except Exception:
        session.rollback()
        raise
