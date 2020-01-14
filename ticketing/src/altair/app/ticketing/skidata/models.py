# -*- coding: utf-8 -*-

import sqlalchemy as sa
import altair.app.ticketing.skidata.utils as utils
from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
from altair.skidata.models import HSHErrorType, HSHErrorNumber
from standardenum import StandardEnum
from datetime import datetime


class SkidataBarcode(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SkidataBarcode'
    id = sa.Column(Identifier, primary_key=True)
    ordered_product_item_token_id = sa.Column(Identifier, sa.ForeignKey('OrderedProductItemToken.id'), nullable=True)
    ordered_product_item_token = sa.orm.relationship('OrderedProductItemToken',
                                                     backref=sa.orm.backref('skidata_barcode', uselist=False))
    data = sa.Column(sa.String(30), nullable=False)
    sent_at = sa.Column(sa.DateTime(), nullable=True)
    canceled_at = sa.Column(sa.DateTime(), nullable=True)

    @staticmethod
    def insert_new_barcode(token_id, session=DBSession):
        """
        SkidataBarcodeに新規にデータをインサートする。
        :param token_id: OrderedProductItemToken.id
        :param session: DBセッション。デフォルトはマスタ。
        :return: 新規生成したSkidataBarcodeデータ
        """
        new_barcode = SkidataBarcode()
        new_barcode.ordered_product_item_token_id = token_id
        new_barcode.data = utils.issue_new_qr_str()
        session.add(new_barcode)
        _flushing(session)
        return new_barcode

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
    def find_by_barcode(data, session=DBSession):
        """
        指定されたQRデータを元にSkidataBarcodeを取得する
        :param data: QRデータ
        :param session: DBセッション。デフォルトはマスタ。
        :return: SkidataBarcodeデータ
        :raises: NoResultFound SkidataBarcodeデータが存在しない場合
        """
        return session.query(SkidataBarcode).filter(SkidataBarcode.data == data).one()

    @staticmethod
    def find_by_token_id(token_id, session=DBSession):
        """
        指定されたOrderedProductItemToken.idを元にSkidataBarcodeを取得する
        :param token_id: OrderedProductItemToken.id
        :param session: DBセッション。デフォルトはマスタ。
        :return: SkidataBarcodeデータ
        :raises: NoResultFound SkidataBarcodeデータが存在しない場合
        """
        return session.query(SkidataBarcode).filter(SkidataBarcode.ordered_product_item_token_id == token_id).one()

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

    @staticmethod
    def update_token(barcode_id, token_id, session=DBSession):
        """
        既存のSkidataBarcodeデータのordered_product_item_token_idを更新する
        :param barcode_id: SkidataBarcode.id
        :param token_id: OrderedProductItemToken.id
        :param session: DBセッション。デフォルトはマスタ。
        """
        barcode = session.query(SkidataBarcode).filter(SkidataBarcode.id == barcode_id).with_lockmode(u'update').one()
        barcode.ordered_product_item_token_id = token_id
        _flushing(session)

    @staticmethod
    def cancel(barcode_id, session=DBSession):
        """
        既存のSkidataBarcodeデータをキャンセルする
        :param barcode_id: SkidataBarcode.id
        :param session: DBセッション。デフォルトはマスタ。
        """
        barcode = session.query(SkidataBarcode).filter(SkidataBarcode.id == barcode_id).with_lockmode(u'update').one()
        barcode.canceled_at = datetime.now()
        _flushing(session)


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
        :param session: DBセッション。デフォルトはマスタ
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

    @staticmethod
    def count_by_prop_id(prop_id, session=DBSession):
        """
        指定したプロパティIDにひもづくデータ数を返す
        :param prop_id: SkidataProperty.id
        :param session: DBセッション。デフォルトはマスタ
        :return: データ数
        """
        return session.query(SkidataPropertyEntry).filter(SkidataPropertyEntry.skidata_property_id==prop_id).count()


class ProtoOPIToken_SkidataBarcode(Base):
    __tablename__ = 'ProtoOPIToken_SkidataBarcode'
    proto_opi_token_id = sa.Column(Identifier, sa.ForeignKey('OrderedProductItemToken.id'), primary_key=True,
                                   nullable=False)
    token = sa.orm.relationship("OrderedProductItemToken", backref="token")
    skidata_barcode_id = sa.Column(Identifier, sa.ForeignKey('SkidataBarcode.id'), nullable=False)

    @staticmethod
    def insert_new_data(skidata_barcode_id, token, session=DBSession):
        """
        新規データをインサートする。
        :param skidata_barcode_id: SkidataBarcode.id
        :param token: OrderedProductItemToken
        :param session: DBセッション。デフォルトはマスタ
        :return: 生成したProtoOPIToken_SkidataBarcodeデータ
        """
        data = ProtoOPIToken_SkidataBarcode()
        data.skidata_barcode_id = skidata_barcode_id
        data.token = token
        session.add(data)
        _flushing(session)
        return data

    @staticmethod
    def find_by_token_id(token_id, session=DBSession):
        """
        指定されたOrderedProductItemToken.idを元にProtoOPIToken_SkidataBarcodeを取得する。
        :param token_id: OrderedProductItemToken.id
        :param session: DBセッション。デフォルトはマスタ
        :return: ProtoOPIToken_SkidataBarcodeデータ
        :raises: NoResultFound データが見つからない場合
        """
        return session.query(ProtoOPIToken_SkidataBarcode) \
            .filter(ProtoOPIToken_SkidataBarcode.proto_opi_token_id == token_id) \
            .one()


class SkidataBarcodeEmailHistory(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SkidataBarcodeEmailHistory'
    id = sa.Column(Identifier, primary_key=True)
    skidata_barcode_id = sa.Column(Identifier, sa.ForeignKey('SkidataBarcode.id'), nullable=False)
    to_address = sa.Column(sa.String(255), nullable=False)
    sent_at = sa.Column(sa.DateTime(), nullable=False)
    skidata_barcode = sa.orm.relationship('SkidataBarcode',
                                          backref=sa.orm.backref("emails", order_by=sent_at.desc(), cascade="all"))

    @staticmethod
    def insert_new_history(skidata_barcode_id, to_address, sent_at, session=DBSession):
        """
        新規に送信履歴をインサートする。
        :param skidata_barcode_id: SkidataBarcode.id
        :param to_address: 送信先メールアドレス
        :param sent_at: 送信日時
        :param session: DBセッション。デフォルトはマスタ
        :return: 生成したSkidataBarcodeEmailHistoryデータ
        """
        new_history = SkidataBarcodeEmailHistory()
        new_history.skidata_barcode_id = skidata_barcode_id
        new_history.to_address = to_address
        new_history.sent_at = sent_at
        session.add(new_history)
        _flushing(session)
        return new_history

    @staticmethod
    def find_all_by_barcode_id(skidata_barcode_id, session=DBSession):
        """
        指定されたSkidataBarcode.idを元に全てのSkidataBarcodeEmailHistoryを取得する
        :param skidata_barcode_id: SkidataBarcode.id
        :param session: DBセッション。デフォルトはマスタ
        :return: SkidataBarcodeEmailHistoryのリスト
        """
        return session.query(SkidataBarcodeEmailHistory).filter(
            SkidataBarcodeEmailHistory.skidata_barcode_id == skidata_barcode_id).all()


class SkidataBarcodeErrorHistory(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SkidataBarcodeErrorHistory'
    id = sa.Column(Identifier, primary_key=True)
    skidata_barcode_id = sa.Column(Identifier, sa.ForeignKey('SkidataBarcode.id'), nullable=False)
    type = sa.Column(sa.String(1), nullable=False)
    number = sa.Column(sa.INT(11), nullable=False)
    description = sa.Column(sa.String(255), nullable=True)
    skidata_barcode = sa.orm.relationship(
        'SkidataBarcode',
        backref=sa.orm.backref("errors",
                               order_by="desc(SkidataBarcodeErrorHistory.created_at)",
                               cascade="all")
    )

    @staticmethod
    def insert_new_history(skidata_barcode_id, hsh_error_type, hsh_error_number, description=None, session=DBSession):
        """
        新規にSkidata連携エラー履歴をインサートする。
        :param skidata_barcode_id: SkidataBarcode.id

        :param hsh_error_type: エラータイプ
        :type hsh_error_type: HSHErrorType or str

        :param hsh_error_number: エラーナンバー
        :type hsh_error_number: HSHErrorNumber or int

        :param description: エラーメッセージ
        :type description: str

        :param session: DBセッション。デフォルトはマスタ

        :return: 生成したSkidataBarcodeErrorHistoryデータ
        """
        new_history = SkidataBarcodeErrorHistory()
        new_history.skidata_barcode_id = skidata_barcode_id
        new_history.type = hsh_error_type.value \
            if isinstance(hsh_error_type, HSHErrorType) else hsh_error_type
        new_history.number = hsh_error_number.value \
            if isinstance(hsh_error_number, HSHErrorNumber) else hsh_error_number
        new_history.description = description
        session.add(new_history)
        _flushing(session)
        return new_history

    @staticmethod
    def find_all_by_barcode_id(skidata_barcode_id, session=DBSession):
        """
        指定されたSkidataBarcode.idを元に全てのSkidataBarcodeErrorHistoryを取得する
        :param skidata_barcode_id: SkidataBarcode.id
        :param session: DBセッション。デフォルトはマスタ
        :return: SkidataBarcodeErrorHistoryのリスト
        """
        return session.query(SkidataBarcodeErrorHistory).filter(
            SkidataBarcodeErrorHistory.skidata_barcode_id == skidata_barcode_id).all()


def _flushing(session):
    try:
        session.flush()
    except Exception:
        session.rollback()
        raise
