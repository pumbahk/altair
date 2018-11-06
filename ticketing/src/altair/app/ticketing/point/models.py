# -*- coding: utf-8 -*-

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
    order_id = sa.Column(Identifier, sa.ForeignKey('Order.id'), unique=True, nullable=False)
    order_no = sa.Column(sa.Unicode(255), nullable=False)
    order = sa.orm.relationship('Order')  # order_idにはUnique制限があるのでOne to Oneとなる
    group_id = sa.Column(sa.Integer, nullable=False)
    reason_id = sa.Column(sa.Integer, nullable=False)
    point_status = sa.Column(sa.SmallInteger, nullable=False)
    auth_point = sa.Column(sa.Integer, nullable=False)
    authed_at = sa.Column(sa.DateTime, default=None, nullable=True)
    fix_point = sa.Column(sa.Integer, nullable=True)
    fixed_at = sa.Column(sa.DateTime, default=None, nullable=True)
    canceled_at = sa.Column(sa.DateTime, default=None, nullable=True)

    @staticmethod
    def create_point_redeem(point_redeem):
        """
        PointRedeemテーブルの新規レコードを登録します。
        :param point_redeem: PointRedeemインスタンス
        :return: Insertしたレコードの主キー
        """
        point_redeem.add()
        return point_redeem.id

    @staticmethod
    def get_point_redeem(unique_id=None, order_id=None, order_no=None):
        """
        PointRedeemテーブルのレコードを取得します。
        ユニークキーのいずれかを引数に渡せば結果を取得できます。
        :param unique_id: ポイントユニークID
        :param order_id: Orderテーブルの主キー
        :param order_no: 予約番号
        :return: selectしたPointRedeemテーブルのレコード
        """
        if unique_id is not None:
            point_redeem = DBSession.query(PointRedeem).filter(PointRedeem.unique_id == unique_id)
        elif order_id is not None:
            point_redeem = DBSession.query(PointRedeem).filter(PointRedeem.order_id == order_id)
        else:
            point_redeem = DBSession.query(PointRedeem).filter(PointRedeem.order_no == order_no)

        return point_redeem.first()

    @staticmethod
    def update_point_redeem(point_redeem):
        """
        PointRedeemテーブルの対象レコードを更新します。
        :param point_redeem: PointRedeemインスタンス
        """
        point_redeem.update()

    @staticmethod
    def delete_point_redeem(point_redeem):
        """
        PointRedeemテーブルの対象レコードを論理削除します。
        :param point_redeem: PointRedeemインスタンス
        """
        point_redeem.delete()


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
