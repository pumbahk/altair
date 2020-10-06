# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
from altair.saannotation import AnnotatedColumn
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Boolean, DateTime, Unicode, UnicodeText
from sqlalchemy.sql.expression import desc

logger = logging.getLogger(__name__)


def session_flush(session):
    try:
        session.flush()
    except Exception:
        session.rollback()
        raise


class RakutenTvSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    Rakuten TV 環境情報
    """
    __tablename__ = 'RakutenTvSetting'

    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=(u'ID'))

    performance_id = AnnotatedColumn(Identifier, nullable=False, index=True, _a_label=(u'パフォーマンスID'))

    available_flg = AnnotatedColumn(Boolean, nullable=False, default=False, server_default='0', _a_label=(u'使用可否'))
    rtv_endpoint_url = AnnotatedColumn(Unicode(512), nullable=False, _a_label=(u'視聴用URL'), default=u'')

    release_date = AnnotatedColumn(DateTime, nullable=True, _a_label=u'URL公開日時')

    description = AnnotatedColumn(UnicodeText, nullable=True, default=None, _a_label=(u'説明'))

    @staticmethod
    def insert_rakuten_tv_setting(rakuten_tv_setting, session=None):
        """
        RakutenTvSettingテーブルの新規レコードを登録します。
        :param rakuten_tv_setting: RakutenTvSettingインスタンス
        :param session: DBセッション
        :return: Insertしたレコードの主キー
        """
        if session is None:
            session = DBSession

        session.add(rakuten_tv_setting)
        session_flush(session)

        return rakuten_tv_setting.id

    @staticmethod
    def update_rakuten_tv_setting(rakuten_tv_setting, session=None):
        """
        RakutenTvSettingテーブルの対象レコードを更新します。
        :param rakuten_tv_setting: RakutenTvSettingインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        rakuten_tv_setting.updated_at = datetime.now()
        session.merge(rakuten_tv_setting)
        session_flush(session)

    @staticmethod
    def delete_rakuten_tv_setting(rakuten_tv_setting, session=None):
        """
        RakutenTvSettingテーブルの対象レコードを論理削除します。
        :param rakuten_tv_setting: RakutenTvSettingインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        rakuten_tv_setting.deleted_at = datetime.now()
        session.merge(rakuten_tv_setting)
        session_flush(session)

    @staticmethod
    def find_by_id(id, session=None):
        """
        指定されたidを元にRakutenTvSettingを取得する。
        :param id: 主キー
        :param session: DBセッション
        :return: RakutenTvSettingデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSetting).filter(RakutenTvSetting.id == id).first()


    @staticmethod
    def find_by_performance_id(performance_id, session=None):
        """
        指定されたperformance_idを元にRakutenTvSettingを取得する。
        :param performance_id: パフォーマンスID
        :param session: DBセッション
        :return: RakutenTvSettingデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSetting)\
            .filter(RakutenTvSetting.performance_id == performance_id)\
            .order_by(desc(RakutenTvSetting.id))\
            .first()

    @staticmethod
    def confirm_available_flg(performance_id, session=None):
        """
        指定されたperformance_idを元にRakutenTvSettingを取得する。
        :param performance_id: パフォーマンスID
        :param session: DBセッション
        :return: RakutenTvSettingデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSetting)\
            .filter(RakutenTvSetting.performance_id == performance_id)\
            .filter(RakutenTvSetting.available_flg == False) \
            .order_by(desc(RakutenTvSetting.id))\
            .first()


class RakutenTvSalesData(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    Rakuten TV 販売情報
    """
    __tablename__ = 'RakutenTvSalesData'

    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=(u'ID'))

    rakuten_tv_setting_id = AnnotatedColumn(Identifier, nullable=False, index=True, _a_label=(u'RakutenTvSetting環境情報ID'))

    performance_id = AnnotatedColumn(Identifier, nullable=False, index=True, _a_label=(u'パフォーマンスID'))

    order_no = AnnotatedColumn(Unicode(255), nullable=False, _a_label=(u'注文番号'))

    easy_id = AnnotatedColumn(Unicode(16), nullable=False, _a_label=(u'楽天会員ID'), default=u'')

    paid_at = AnnotatedColumn(DateTime, nullable=True, default=None, _a_label=(u'決済日時'))
    canceled_at = AnnotatedColumn(DateTime, nullable=True, default=None, _a_label=(u'キャンセル日時'))
    refunded_at = AnnotatedColumn(DateTime, nullable=True, default=None, _a_label=(u'払戻日時'))

    @staticmethod
    def insert_rakuten_tv_sales_data(rakuten_tv_sales_data, session=None):
        """
        RakutenTvSalesDataテーブルの新規レコードを登録します。
        :param rakuten_tv_sales_data: RakutenTvSalesDataインスタンス
        :param session: DBセッション
        :return: Insertしたレコードの主キー
        """
        if session is None:
            session = DBSession

        session.add(rakuten_tv_sales_data)
        session_flush(session)

        return rakuten_tv_sales_data.id

    @staticmethod
    def update_rakuten_tv_sales_data(rakuten_tv_sales_data, session=None):
        """
        RakutenTvSalesDataテーブルの対象レコードを更新します。
        :param rakuten_tv_sales_data: RakutenTvSalesDataインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        rakuten_tv_sales_data.updated_at = datetime.now()
        session.merge(rakuten_tv_sales_data)
        session_flush(session)

    @staticmethod
    def delete_rakuten_tv_sales_data(rakuten_tv_sales_data, session=None):
        """
        RakutenTvSalesDataテーブルの対象レコードを論理削除します。
        :param rakuten_tv_sales_data: RakutenTvSalesDataインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        rakuten_tv_sales_data.deleted_at = datetime.now()
        session.merge(rakuten_tv_sales_data)
        session_flush(session)

    @staticmethod
    def find_by_id(id, session=None):
        """
        指定されたidを元にRakutenTvSalesDataを取得する。
        :param id: 主キー
        :param session: DBセッション
        :return: RakutenTvSalesDataデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSalesData).filter(RakutenTvSalesData.id == id).first()

    @staticmethod
    def find_by_performance_id_and_easy_id(performance_id, easy_id, session=None):
        """
        指定されたperformance_idとeasy_idを元にRakutenTvSalesDataを取得する。
        :param performance_id: パフォーマンスID
        :param easy_id: 楽天会員ID
        :param session: DBセッション
        :return: RakutenTvSalesDataデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSalesData)\
            .filter(RakutenTvSalesData.performance_id == performance_id)\
            .filter(RakutenTvSalesData.easy_id == easy_id)\
            .filter(RakutenTvSalesData.deleted_at.is_(None))\
            .first()

    @staticmethod
    def find_by_performance_id(performance_id, session=None):
        """
        指定されたperformance_idを元にRakutenTvSalesDataを取得する。
        :param performance_id: パフォーマンスID
        :param session: DBセッション
        :return: RakutenTvSalesDataデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSalesData)\
            .filter(RakutenTvSalesData.performance_id == performance_id)\
            .filter(RakutenTvSalesData.deleted_at.is_(None))\
            .order_by(desc(RakutenTvSalesData.id))\
            .first()

    @staticmethod
    def find_by_easy_id(easy_id, session=None):
        """
        指定されたeasy_idを元にRakutenTvSalesDataを取得する。
        :param easy_id: 楽天会員ID
        :param session: DBセッション
        :return: RakutenTvSalesDataデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSalesData)\
            .filter(RakutenTvSalesData.easy_id == easy_id)\
            .filter(RakutenTvSalesData.deleted_at.is_(None))\
            .order_by(desc(RakutenTvSalesData.id))\
            .first()

    @staticmethod
    def is_comfirm_paid_at(performance_id, easy_id, session=None):
        """
        指定されたeasy_idを元にRakutenTvSalesData.paid_atを取得する。
        :param performance_id: パフォーマンスID
        :param easy_id: 楽天会員ID
        :param session: DBセッション
        :return: RakutenTvSalesData.paid_atデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSalesData)\
            .join(RakutenTvSetting)\
            .filter(RakutenTvSetting.performance_id == performance_id) \
            .filter(RakutenTvSalesData.easy_id == easy_id) \
            .filter(RakutenTvSalesData.paid_at.is_(None)) \
            .first()

    @staticmethod
    def is_comfirm_canceled_at(performance_id, easy_id, session=None):
        """
        指定されたeasy_idを元にRakutenTvSalesData.canceled_atを取得する。
        :param performance_id: パフォーマンスID
        :param easy_id: 楽天会員ID
        :param session: DBセッション
        :return: RakutenTvSalesData.canceled_atデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSalesData.canceled_at)\
            .join(RakutenTvSetting) \
            .filter(RakutenTvSetting.performance_id == performance_id) \
            .filter(RakutenTvSalesData.easy_id == easy_id) \
            .filter(RakutenTvSalesData.canceled_at.isnot(None)) \
            .first()

    @staticmethod
    def is_comfirm_refunded_at(performance_id, easy_id, session=None):
        """
        指定されたeasy_idを元にRakutenTvSalesData.refunded_atを取得する。
        :param performance_id: パフォーマンスID
        :param easy_id: 楽天会員ID
        :param session: DBセッション
        :return: RakutenTvSalesData.refunded_atデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSalesData.refunded_at)\
            .join(RakutenTvSetting) \
            .filter(RakutenTvSetting.performance_id == performance_id) \
            .filter(RakutenTvSalesData.easy_id == easy_id) \
            .filter(RakutenTvSalesData.refunded_at.isnot(None)) \
            .first()

    @staticmethod
    def rakuten_tv_sales_data_paid_at(rakuten_tv_sales_data, session=None):
        """
        RakutenTvSalesDataテーブル対象レコードの決済日時をセットします。
        :param rakuten_tv_sales_data: RakutenTvSalesDataインスタンス
        :param session: DBセッション
        :return: 日時をセットしたRakutenTvSalesDataデータ
        """
        if session is None:
            session = DBSession

        rakuten_tv_sales_data.paid_at = datetime.now()
        session.merge(rakuten_tv_sales_data)
        session_flush(session)

        return rakuten_tv_sales_data

    @staticmethod
    def rakuten_tv_sales_data_canceled_at(rakuten_tv_sales_data, session=None):
        """
        RakutenTvSalesDataテーブル対象レコードのキャンセル日時をセットします。
        :param rakuten_tv_sales_data: RakutenTvSalesDataインスタンス
        :param session: DBセッション
        :return: 日時をセットしたRakutenTvSalesDataデータ
        """
        if session is None:
            session = DBSession

        rakuten_tv_sales_data.canceled_at = datetime.now()
        session.merge(rakuten_tv_sales_data)
        session_flush(session)

        return rakuten_tv_sales_data

    @staticmethod
    def rakuten_tv_sales_data_refunded_at(rakuten_tv_sales_data, session=None):
        """
        RakutenTvSalesDataテーブル対象レコードの払戻日時をセットします。
        :param rakuten_tv_sales_data: RakutenTvSalesDataインスタンス
        :param session: DBセッション
        :return: 日時をセットしたRakutenTvSalesDataデータ
        """
        if session is None:
            session = DBSession

        rakuten_tv_sales_data.refunded_at = datetime.now()
        session.merge(rakuten_tv_sales_data)
        session_flush(session)

        return rakuten_tv_sales_data

    @staticmethod
    def find_by_order_no_and_performance_id(order_no, performance_id, session=None):
        """
        指定されたorder_noとperformance_idを元にRakutenTvSalesDataを取得する。
        :param order_no: 注文番号
        :param performance_id: パフォーマンスID
        :param session: DBセッション
        :return: RakutenTvSalesDataデータ
        """
        if session is None:
            session = DBSession

        return session.query(RakutenTvSalesData) \
            .filter(RakutenTvSalesData.order_no == order_no)\
            .filter(RakutenTvSalesData.easy_id.isnot(None))\
            .filter(RakutenTvSalesData.performance_id == performance_id) \
            .filter(RakutenTvSalesData.refunded_at.is_(None))\
            .filter(RakutenTvSalesData.canceled_at.is_(None))\
            .filter(RakutenTvSalesData.deleted_at.is_(None))\
            .order_by(desc(RakutenTvSalesData.id)).first()
