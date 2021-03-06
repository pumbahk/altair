# -*- coding: utf-8 -*-
import sqlalchemy as sa

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
from standardenum import StandardEnum

class ReviewAuthorizationTypeEnum(StandardEnum):
    """num
    Review_Authorization_Type Enum Class.
    - CART : カート
    - LOTS : 抽選
    """
    CART = 1  # カート
    LOTS = 2  # 抽選


class ReviewAuthorization(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    ReviewAuthorization Table Class.
    """
    __tablename__ = 'ReviewAuthorization'
    id = sa.Column(Identifier, primary_key=True)
    order_no = sa.Column(sa.Unicode(255), nullable=False)
    review_password = sa.Column(sa.Unicode(255), nullable=False)
    email = sa.Column(sa.Unicode(255), index=True, nullable=False)
    type = sa.Column(sa.Boolean, nullable=False, default=False)

    @staticmethod
    def create_review_authorization(review_authorization):
        """
        ReviewAuthorizationテーブルの新規レコードを登録します。
        :param review_authorization: ReviewAuthorizationインスタンス
        :return: Insertしたレコードの主キー
        """

        DBSession.add(review_authorization)
        try:
            DBSession.flush()
        except:
            DBSession.rollback()
            raise

        return review_authorization.id
