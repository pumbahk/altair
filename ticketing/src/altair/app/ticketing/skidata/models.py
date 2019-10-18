# -*- coding: utf-8 -*-

import sqlalchemy as sa
import altair.app.ticketing.skidata.utils as utils
from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
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
    SalesSegmentGroup = 0  # 販売区分グループ向けのプロパティを意味する
    ProductItem = 1  # 商品明細向けのプロパティを意味する


class SkidataProperty(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SkidataProperty'
    id = sa.Column(Identifier, primary_key=True)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'), nullable=False)
    organization = sa.orm.relationship('Organization')
    prop_type = sa.Column(sa.SmallInteger(), nullable=False)
    name = sa.Column(sa.String(30), nullable=False)
    value = sa.Column(sa.SmallInteger(), nullable=False)

    @staticmethod
    def find_by_id(prop_id, session=DBSession):
        """
        指定されたIDを元にSkidataPropertyデータを取得する
        :param prop_id: SkidataProperty.id
        :param session: DBSession。デフォルトはマスタ
        :return: SkidataPropertyデータ
        :raises: NoResultFound データが見つからない場合
        """
        return session.query(SkidataProperty).filter(SkidataProperty.id == prop_id).one()

    @staticmethod
    def update_property(prop_id, name, value, session=DBSession):
        """
        指定されたSkidataPropertyの内容を更新する
        :param prop_id: SkidataProperty.id
        :param name: プロパティ名
        :param value: プロパティ値
        :param session: DBセッション。デフォルトはマスタ
        :return: 更新したSkidataProperty
        :raises: NoResultFound データが見つからない場合
        """
        prop = session.query(SkidataProperty).filter(SkidataProperty.id == prop_id).with_lockmode('update').one()
        prop.name = name
        prop.value = value
        _flushing(session)
        return prop

    @staticmethod
    def delete_property(prop_id, session=DBSession):
        """
        指定されたSkidataPropertyを削除する
        :param prop_id:  SkidataProperty.id
        :param session: DBセッション。デフォルトはマスタ
        :raises: NoResultFound データが見つからない場合
        """
        prop = session.query(SkidataProperty).filter(SkidataProperty.id == prop_id).with_lockmode('update').one()
        prop.delete()
        _flushing(session)

    @staticmethod
    def find_all_by_org_id(organization_id, session=DBSession):
        """
        指定されたOrganization.idを元に全てのSkidataPropertyデータを取得する
        :param organization_id: Organization.id
        :param session: DBセッション。デフォルトはマスタ。
        :return: SkidataPropertyデータのリスト
        """
        return session.query(SkidataProperty).filter(SkidataProperty.organization_id == organization_id).all()

    @staticmethod
    def find_sales_segment_group_props(organization_id, session=DBSession):
        """
        販売区分グループ向けのSkidataPropertyを取得する。
        :param organization_id: Organization.id
        :param session: DBセッション。デフォルトはマスタ。
        :return: SkidataPropertyデータのリスト
        """
        return session.query(SkidataProperty)\
            .filter(SkidataProperty.organization_id == organization_id)\
            .filter(SkidataProperty.prop_type == SkidataPropertyTypeEnum.SalesSegmentGroup.v)\
            .all()

    @staticmethod
    def find_product_item_props(organization_id, session=DBSession):
        """
        商品明細向けのSkidataPropertyを取得する。
        :param organization_id: Organization.id
        :param session: DBセッション。デフォルトはマスタ。
        :return: SkidataPropertyデータのリスト
        """
        return session.query(SkidataProperty)\
            .filter(SkidataProperty.organization_id == organization_id)\
            .filter(SkidataProperty.prop_type == SkidataPropertyTypeEnum.ProductItem.v)\
            .all()

    @staticmethod
    def insert_new_property(organization_id, name, value, prop_type, session=DBSession):
        """
        指定値を元にSkidataPropertyを新規にインサートする。
        :param organization_id: Organization.id
        :param name: プロパティ名
        :param value: プロパティ値
        :param prop_type: プロパティのタイプ(SkidataPropertyTypeEnumの数値を指定)
        :param session: DBセッション。デフォルトはマスタ。
        :return: 生成されたSkidataProperty
        """
        prop = SkidataProperty()
        prop.organization_id = organization_id
        prop.name = name
        prop.value = value
        prop.prop_type = prop_type

        session.add(prop)
        _flushing(session)
        return prop


class SkidataPropertyEntry(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SkidataPropertyEntry'
    id = sa.Column(Identifier, primary_key=True)
    skidata_property_id = sa.Column(Identifier, sa.ForeignKey('SkidataProperty.id'), nullable=False)
    property = sa.orm.relationship('SkidataProperty')
    related_id = sa.Column(Identifier, nullable=False)

    @staticmethod
    def insert_new_entry(prop_id, related_id, session=DBSession):
        """
        指定された内容を元にSkidataPropertyEntryを新規にインサートする
        :param prop_id: SkidataProperty.id
        :param related_id: 関連テーブルの主キー
        :param session: DBセッション。デフォルトはマスタ。
        :return: インサートされたSkidataPropertyEntry
        """
        entry = SkidataPropertyEntry()
        entry.skidata_property_id = prop_id
        entry.related_id = related_id

        session.add(entry)
        _flushing(session)
        return entry

    @staticmethod
    def update_entry_for_sales_segment_group(sales_segment_group_id, prop_id_to_update, session=DBSession):
        """
        指定された販売区分グループに紐付くSkidataPropertyEntryを更新する
        :param sales_segment_group_id: SalesSegmentGroup.id
        :param prop_id_to_update: 更新後のSkidataProperty.id
        :param session: DBセッション。通常はマスタ。
        :return: 更新したSkidataPropertyEntry
        :raises: NoResultFound データが見つからない場合
        """
        return SkidataPropertyEntry.update_entry_by_prop_type(
            sales_segment_group_id, prop_id_to_update, SkidataPropertyTypeEnum.SalesSegmentGroup.v, session)

    @staticmethod
    def update_entry_for_product_item(product_item_id, prop_id_to_update, session=DBSession):
        """
        指定された商品明細に紐付くSkidataPropertyEntryを更新する
        :param product_item_id: ProductItem.id
        :param prop_id_to_update: 更新後のSkidataProperty.id
        :param session: DBセッション。通常はマスタ。
        :return: 更新したSkidataPropertyEntry
        :raises: NoResultFound データが見つからない場合
        """
        return SkidataPropertyEntry.update_entry_by_prop_type(
            product_item_id, prop_id_to_update, SkidataPropertyTypeEnum.ProductItem.v, session)

    @staticmethod
    def update_entry_by_prop_type(related_id, prop_id_to_update, prop_type, session=DBSession):
        """
        指定されたタイプに紐付くSkidataPropertyEntryを更新する
        :param related_id: SkidataPropertyEntry.related_id
        :param prop_id_to_update: 更新後のSkidataProperty.id
        :param prop_type: SkidataPropertyEntry.prop_type
        :param session: DBセッション。通常はマスタ。
        :return: 更新したSkidataPropertyEntry
        :raises: NoResultFound データが見つからない場合
        """
        entry = session.query(SkidataPropertyEntry) \
            .join(SkidataProperty) \
            .filter(SkidataPropertyEntry.related_id == related_id) \
            .filter(SkidataProperty.prop_type == prop_type) \
            .with_lockmode('update') \
            .one()

        entry.skidata_property_id = prop_id_to_update
        _flushing(session)
        return entry

    @staticmethod
    def delete_entry_for_sales_segment_group(sales_segment_group_id, session=DBSession):
        """
        指定された販売区分グループに紐付くSkidataPropertyEntryを削除する
        :param sales_segment_group_id: SalesSegmentGroup.id
        :param session: DBセッション。デフォルトはマスタ。
        :raises: NoResultFound データが見つからない場合
        """
        SkidataPropertyEntry.delete_entry_by_prop_type(
            sales_segment_group_id, SkidataPropertyTypeEnum.SalesSegmentGroup.v, session)

    @staticmethod
    def delete_entry_for_product_item(product_item_id, session=DBSession):
        """
        指定された商品明細に紐付くSkidataPropertyEntryを削除する
        :param product_item_id: ProductItem.id
        :param session: DBセッション。デフォルトはマスタ。
        :raises: NoResultFound データが見つからない場合
        """
        SkidataPropertyEntry.delete_entry_by_prop_type(product_item_id, SkidataPropertyTypeEnum.ProductItem.v, session)

    @staticmethod
    def delete_entry_by_prop_type(related_id, prop_type, session=DBSession):
        """
        指定されたタイプにひもづくSkidataPropertyEntryを削除する
        :param related_id: SkidataPropertyEntry.related_id
        :param prop_type: SkidataPropertyEntry.prop_type
        :param session: session: DBセッション。デフォルトはマスタ
        :raises: NoResultFound データが見つからない場合
        """
        entry = session.query(SkidataPropertyEntry) \
            .join(SkidataProperty) \
            .filter(SkidataPropertyEntry.related_id == related_id) \
            .filter(SkidataProperty.prop_type == prop_type) \
            .with_lockmode('update') \
            .one()

        entry.delete()
        _flushing(session)


def _flushing(session):
    try:
        session.flush()
    except Exception:
        session.rollback()
        raise
