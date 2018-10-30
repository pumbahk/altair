# -*- coding: utf-8 -*-

import sqlalchemy as sa
import sqlahelper

from altair.models import Identifier
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

session = sqlahelper.get_session()
Base = sqlahelper.get_base()


class PointRedeem(Base):
    """
    PointRedeemテーブルのクラスです。
    """
    __tablename__ = 'PointRedeem'
    id = sa.Column(Identifier, primary_key=True)
    easy_id = sa.Column(sa.Unicode(16), nullable=False)
    unique_id = sa.Column(Identifier, nullable=False)
    order_id = sa.Column(Identifier, nullable=False)
    order_no = sa.Column(sa.Unicode(255), nullable=False)
    group_id = sa.Column(sa.Integer, nullable=False)
    reason_id = sa.Column(sa.Integer, nullable=False)
    point_status = sa.Column(sa.Integer, nullable=False)
    auth_point = sa.Column(sa.Integer, nullable=False)
    authed_at = sa.Column(sa.DateTime, default=None, nullable=False)
    fix_point = sa.Column(sa.Integer, nullable=True)
    fixed_at = sa.Column(sa.DateTime, nullable=True)
    canceled_at = sa.Column(sa.DateTime, nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False)
    deleted_at = sa.Column(sa.DateTime, nullable=True)

    @staticmethod
    def create_point_redeem(point_redeem):
        """
        PointRedeemテーブルの新規レコードを登録します。
        :param point_redeem: PointRedeemインスタンス
        :return: Insertしたレコードの主キー
        """
        session.add(point_redeem)
        session.flush()
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
            point_redeem = session.query(PointRedeem).filter(PointRedeem.unique_id == unique_id)
        elif order_id is not None:
            point_redeem = session.query(PointRedeem).filter(PointRedeem.order_id == order_id)
        else:
            point_redeem = session.query(PointRedeem).filter(PointRedeem.order_no == order_no)

        try:
            return point_redeem.one()
        except NoResultFound:
            return None

    @staticmethod
    def update_point_redeem(point_redeem):
        """
        PointRedeemテーブルの対象レコードを更新します。
        :param point_redeem: PointRedeemインスタンス
        :return: 更新結果
        """
        session.merge(point_redeem)
        session.flush()
        return True

    @staticmethod
    def delete_point_redeem(point_redeem):
        """
        PointRedeemテーブルの対象レコードを論理削除します。
        :param point_redeem: PointRedeemインスタンス
        :return: 論理削除結果
        """
        point_redeem.deleted_at = datetime.now()
        session.merge(point_redeem)
        session.flush()
        return True
