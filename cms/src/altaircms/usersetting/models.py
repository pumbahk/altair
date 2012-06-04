# coding: utf-8
#
# ユーザ管理関連のモデル
#
from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Integer, DateTime, String, Unicode

from altaircms.models import Base

class User(Base):
    """
    サイト利用者
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    email = Column(String(255))
    site_id = Column(Integer, ForeignKey("site.id"))
    is_active = Column(Integer, default=1)
    is_administrator = Column(Integer, default=0)

    billinghistory = relationship("BillingHistory", backref="user")


class BillingHistory(Base):
    """
    購入履歴
    """
    __tablename__ = 'order_history'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    ticket_id = Column(Integer, ForeignKey("ticket.id"))

    user_id = Column(Integer, ForeignKey("user.id"))


class MailMagazine(Base):
    """
    メルマガマスタ
    """
    __tablename__ = 'mailmagazine'
    id = Column(Integer, primary_key=True)

    title = Column(Unicode(255)) # メルマガタイトル
    description = Column(Unicode(255)) # メルマガ説明

    site_id = Column(Integer, ForeignKey("site.id"))


class MailMagazineUser(Base):
    """
    メルマガと参加者の対応表
    """
    __tablename__ = 'mailmagazine_user'

    id = Column(Integer, primary_key=True)

    mailmagazine_id = Column(Integer, ForeignKey('mailmagazine.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    joined_at = Column(DateTime, default=datetime.now())
    can_distribute = Column(Integer, default=0)


class MailMagazineDistribute(Base):
    """
    配信ジョブテーブル
    """
    __tablename__ = 'mailmagazine_distribute'

    id = Column(Integer, primary_key=True)

    mailmagazine_id = Column(Integer, ForeignKey('mailmagazine.id'))
    username = Column(Unicode(255))
    email = Column(String(255))

    status = Column(String(255)) # 配信状態
    send_at = Column(DateTime) # 配信予定
