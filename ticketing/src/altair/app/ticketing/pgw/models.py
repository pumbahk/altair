# -*- coding: utf-8 -*-
import sqlalchemy as sa
from datetime import datetime
from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
from standardenum import StandardEnum


class PGWOrderStatus(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    PGWOrderStatusテーブルのクラスです。
    """
    __tablename__ = 'PGWOrderStatus'
    id = sa.Column(Identifier, primary_key=True)
    pgw_sub_service_id = sa.Column(sa.Unicode(50), nullable=True)
    payment_id = sa.Column(sa.Unicode(255), nullable=False)
    card_token = sa.Column(sa.Unicode(50), nullable=False)
    cvv_token = sa.Column(sa.Unicode(50), nullable=False)
    enrolled_at = sa.Column(sa.DateTime, default=None, nullable=False)
    authed_at = sa.Column(sa.DateTime, default=None, nullable=False)
    captured_at = sa.Column(sa.DateTime, default=None, nullable=False)
    canceled_at = sa.Column(sa.DateTime, default=None, nullable=False)
    refunded_at = sa.Column(sa.DateTime, default=None, nullable=False)
    payment_status = sa.Column(sa.SmallInteger, nullable=False)
    gross_amount = sa.Column(sa.Integer, nullable=False)

    @staticmethod
    def insert_pgw_order_status(pgw_order_status, session=None):
        """
        PGWOrderStatusテーブルの新規レコードを登録します。
        :param pgw_order_status: PGWOrderStatusインスタンス
        :param session: DBセッション
        :return: Insertしたレコードの主キー
        """
        if session is None:
            session = DBSession

        session.add(pgw_order_status)
        _flushing(session)

        return pgw_order_status.id

    @staticmethod
    def get_pgw_order_status(payment_id, session=None):
        """
        PGWOrderStatusテーブルのレコードを取得します。
        :param payment_id: 予約番号(cart:order_no, lots:entry_no)
        :param session: DBセッション
        :return: selectしたPGWOrderStatusテーブルのレコード
        """
        if session is None:
            session = DBSession

        pgw_order_status = session.query(PGWOrderStatus).filter(PGWOrderStatus.payment_id == payment_id)

        return pgw_order_status.first()

    @staticmethod
    def update_pgw_order_status(pgw_order_status, session=None):
        """
        PGWOrderStatusテーブルの対象レコードを更新します。
        :param pgw_order_status: PGWOrderStatusインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        pgw_order_status.updated_at = datetime.now()
        session.merge(pgw_order_status)
        _flushing(session)

    @staticmethod
    def delete_pgw_order_status(pgw_order_status, session=None):
        """
        PGWOrderStatusテーブルの対象レコードを論理削除します。
        :param pgw_order_status: PGWOrderStatusインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        pgw_order_status.deleted_at = datetime.now()
        session.merge(pgw_order_status)
        _flushing(session)


def _flushing(session):
    try:
        session.flush()
    except:
        session.rollback()
        raise


class PaymentStatusEnum(StandardEnum):
    """
    payment_statusのEnumクラスです。
    """
    initialized = 0  # 未オーソリ
    auth = 1  # オーソリ済
    auth_cancel = 2  # オーソリ済(キャンセル対象)
    capture = 3  # 請求済み
    cancel = 4  # キャンセル済
    refund = 5  # 払戻済
    error = 6  # 決済エラー
    pending = 7  # pending
