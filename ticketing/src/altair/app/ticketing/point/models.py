# -*- coding: utf-8 -*-

from datetime import datetime

import sqlalchemy as sa

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
from standardenum import StandardEnum


class PointRedeem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    PointRedeemテーブルのクラスです。
    """
    __tablename__ = 'PointRedeem'
    id = sa.Column(Identifier, primary_key=True)
    easy_id = sa.Column(sa.Unicode(16), nullable=False)
    unique_id = sa.Column(Identifier, nullable=False)
    order_no = sa.Column(sa.Unicode(255), sa.ForeignKey('Order.order_no'), nullable=False)
    order = sa.orm.relationship('Order')
    group_id = sa.Column(sa.Integer, nullable=False)
    reason_id = sa.Column(sa.Integer, nullable=False)
    point_status = sa.Column(sa.SmallInteger, nullable=False)
    auth_point = sa.Column(sa.Integer, nullable=False)
    authed_at = sa.Column(sa.DateTime, default=None, nullable=True)
    fix_point = sa.Column(sa.Integer, nullable=True)
    fixed_at = sa.Column(sa.DateTime, default=None, nullable=True)
    canceled_at = sa.Column(sa.DateTime, default=None, nullable=True)

    @staticmethod
    def create_point_redeem(point_redeem, session=None):
        """
        PointRedeemテーブルの新規レコードを登録します。
        :param point_redeem: PointRedeemインスタンス
        :param session: DBセッション
        :return: Insertしたレコードの主キー
        """
        if session is None:
            session = DBSession

        session.add(point_redeem)
        _flushing(session)

        return point_redeem.id

    @staticmethod
    def get_point_redeem(unique_id=None, order_no=None, session=None, include_deleted=False):
        """
        PointRedeemテーブルのレコードを取得します。
        ユニークキーのいずれかを引数に渡せば結果を取得できます。
        :param unique_id: ポイントユニークID
        :param order_no: 予約番号
        :param session: DBセッション
        :param include_deleted: 論理削除可否
        :return: selectしたPointRedeemテーブルのレコード
        """
        if session is None:
            session = DBSession

        if unique_id is not None:
            point_redeem = session.query(PointRedeem).filter(PointRedeem.unique_id == unique_id)
        else:
            point_redeem = session.query(PointRedeem).filter(PointRedeem.order_no == order_no)

        if include_deleted:
            point_redeem = point_redeem.filter(include_deleted=True)

        return point_redeem.first()

    @staticmethod
    def update_point_redeem(point_redeem, session=None):
        """
        PointRedeemテーブルの対象レコードを更新します。
        :param point_redeem: PointRedeemインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        point_redeem.updated_at = datetime.now()
        session.merge(point_redeem)
        _flushing(session)

    @staticmethod
    def delete_point_redeem(point_redeem, session=None):
        """
        PointRedeemテーブルの対象レコードを論理削除します。
        :param point_redeem: PointRedeemインスタンス
        :param session: DBセッション
        """
        if session is None:
            session = DBSession

        point_redeem.deleted_at = datetime.now()
        session.merge(point_redeem)
        _flushing(session)


def _flushing(session):
    try:
        session.flush()
    except:
        session.rollback()
        raise


class PointStatusEnum(StandardEnum):
    """
    point_statusのEnumクラスです。
    - rollback : altair.point.api:rollbackをリクエストした際に更新するステータスです。
    - auth : altair.point.api:auth_stdonlyをリクエストした際に更新するステータスです。
    - fix : altair.point.api:fixをリクエストした際に更新するステータスです。
    - cancel : altair.point.api:cancelをリクエストした際に更新するステータスです。
    """
    rollback = 0  # ロールバック
    auth = 1  # オーソリ済
    fix = 2  # Fix済
    cancel = 3  # キャンセル
