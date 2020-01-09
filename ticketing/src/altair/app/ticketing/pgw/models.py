# -*- coding: utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
from standardenum import StandardEnum

# 内部トランザクション用
_session = orm.scoped_session(orm.sessionmaker(autocommit=True))


class PGWOrderStatus(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    PGWOrderStatusテーブルのクラスです。
    """
    __tablename__ = 'PGWOrderStatus'
    id = sa.Column(Identifier, primary_key=True)
    pgw_sub_service_id = sa.Column(sa.Unicode(50), nullable=False)
    payment_id = sa.Column(sa.Unicode(255), nullable=False)
    card_token = sa.Column(sa.Unicode(50), nullable=False)
    cvv_token = sa.Column(sa.Unicode(50), nullable=False)
    enrolled_at = sa.Column(sa.DateTime, default=None, nullable=True)
    authed_at = sa.Column(sa.DateTime, default=None, nullable=True)
    captured_at = sa.Column(sa.DateTime, default=None, nullable=True)
    canceled_at = sa.Column(sa.DateTime, default=None, nullable=True)
    refunded_at = sa.Column(sa.DateTime, default=None, nullable=True)
    payment_status = sa.Column(sa.SmallInteger, nullable=False)
    gross_amount = sa.Column(sa.Integer, nullable=False)
    card_brand_code = sa.Column(sa.Unicode(30), nullable=True)
    card_iin = sa.Column(sa.Unicode(6), nullable=True)
    card_last4digits = sa.Column(sa.Unicode(4), nullable=True)
    ahead_com_cd = sa.Column(sa.Unicode(7), nullable=True)
    approval_no = sa.Column(sa.Unicode(7), nullable=True)

    @staticmethod
    def insert_pgw_order_status(pgw_order_status, session=None):
        """
        PGWOrderStatusテーブルの新規レコードを登録します。
        :param pgw_order_status: PGWOrderStatusインスタンス
        :param session: DBセッション
        :return: Insertしたレコードの主キー
        """
        if session is None:
            session = _session

        session.add(pgw_order_status)
        _flushing(session)

        return pgw_order_status.id

    @staticmethod
    def get_pgw_order_status(payment_id, session=None, for_update=False):
        """
        PGWOrderStatusテーブルのレコードを取得します。
        :param payment_id: 予約番号(cart:order_no, lots:entry_no)
        :param session: DBセッション
        :param for_update: 排他制御フラグ
        :return: selectしたPGWOrderStatusテーブルのレコード
        """
        if session is None:
            session = DBSession

        pgw_order_status_query = session.query(PGWOrderStatus)
        if for_update:
            pgw_order_status_query = pgw_order_status_query.with_lockmode('update')

        pgw_order_status = pgw_order_status_query.filter(PGWOrderStatus.payment_id == payment_id)

        return pgw_order_status.first()

    @staticmethod
    def update_pgw_order_status(pgw_order_status, session=None):
        """
        PGWOrderStatusテーブルの対象レコードを更新します。
        :param pgw_order_status: PGWOrderStatusインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = _session

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
            session = _session

        pgw_order_status.deleted_at = datetime.now()
        session.merge(pgw_order_status)
        _flushing(session)

    @hybrid_property
    def is_authorized(self):
        return self.payment_status == int(PaymentStatusEnum.auth)


class PGWMaskedCardDetail(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    PGWMaskedCardDetailテーブルのクラスです。
    """
    __tablename__ = 'PGWMaskedCardDetail'
    id = sa.Column(Identifier, primary_key=True)
    user_id = sa.Column(Identifier, sa.ForeignKey('User.id'), nullable=False)
    card_token = sa.Column(sa.Unicode(50), nullable=False)
    card_iin = sa.Column(sa.Unicode(6), nullable=False)
    card_last4digits = sa.Column(sa.Unicode(4), nullable=False)
    card_expiration_month = sa.Column(sa.Unicode(2), nullable=False)
    card_expiration_year = sa.Column(sa.Unicode(4), nullable=False)
    card_brand_code = sa.Column(sa.Unicode(30), nullable=False)

    @staticmethod
    def insert_pgw_masked_card_detail(pgw_masked_card_detail, session=None):
        """
        PGWMaskedCardDetailテーブルの新規レコードを登録します。
        :param pgw_masked_card_detail: PGWMaskedCardDetailインスタンス
        :param session: DBセッション
        :return: Insertしたレコードの主キー
        """
        if session is None:
            session = DBSession

        session.add(pgw_masked_card_detail)
        _flushing(session)

        return pgw_masked_card_detail.id

    @staticmethod
    def get_pgw_masked_card_detail(user_id, session=None):
        """
        PGWMaskedCardDetailテーブルのレコードを取得します。
        :param user_id: ユーザID
        :param session: DBセッション
        :return: selectしたPGWMaskedCardDetailテーブルのレコード
        """
        if session is None:
            session = DBSession

        pgw_masked_card_detail = session.query(PGWMaskedCardDetail).filter(PGWMaskedCardDetail.user_id == user_id)

        return pgw_masked_card_detail.first()

    @staticmethod
    def update_pgw_masked_card_detail(pgw_masked_card_detail, session=None):
        """
        PGWMaskedCardDetailテーブルの対象レコードを更新します。
        :param pgw_masked_card_detail: PGWMaskedCardDetailインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        pgw_masked_card_detail.updated_at = datetime.now()
        session.merge(pgw_masked_card_detail)
        _flushing(session)

    @staticmethod
    def delete_pgw_masked_card_detail(pgw_masked_card_detail, session=None):
        """
        PGWMaskedCardDetailテーブルの対象レコードを論理削除します。
        :param pgw_masked_card_detail: PGWMaskedCardDetailインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        pgw_masked_card_detail.deleted_at = datetime.now()
        session.merge(pgw_masked_card_detail)
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
