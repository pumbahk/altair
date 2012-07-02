# coding: utf-8

import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession
from datetime import datetime
from datetime import timedelta
import hashlib

class Event(BaseOriginalMixin, Base):
    """
    イベント

    @TODO: 席図をくっつける
    """
    __tablename__ = "event"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    backend_id = sa.Column(sa.Integer)

    created_at = sa.Column(sa.DateTime, default=datetime.now())
    updated_at = sa.Column(sa.DateTime, default=datetime.now())

    title = sa.Column(sa.Unicode(255))
    subtitle = sa.Column(sa.Unicode(255), default=u"")
    description = sa.Column(sa.Unicode(255), default=u"")
    event_open = sa.Column(sa.DateTime)
    event_close = sa.Column(sa.DateTime)
    deal_open = sa.Column(sa.DateTime)
    deal_close = sa.Column(sa.DateTime)
    is_searchable = sa.Column(sa.Boolean, default=True)

    performers = sa.Column(sa.UnicodeText, doc=u"講演者")
    inquiry_for = sa.Column(sa.Unicode(255), default=u"", doc=u"お問い合わせ先")
    notice = sa.Column(sa.UnicodeText, doc=u"注意事項")
    ticket_pickup = sa.Column(sa.UnicodeText, doc=u"チケット引き取り方法")
    ticket_payment = sa.Column(sa.UnicodeText, doc=u"支払い方法")

    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id"))

    @classmethod
    def near_the_deal_close_query(cls, today, N=7, qs=None):
        """ 現在から販売終了N日前までのqueryを返す"""
        limit_day = today + timedelta(days=N)
        where = (cls.deal_open <= today) & (today <= cls.deal_close) & (cls.deal_close <= limit_day)
        return (qs or cls.query).filter(where)

    @classmethod
    def deal_start_this_week_query(cls, today, offset=None, qs=None):
        """今週販売開始するquery(月曜日を週のはじめとする)"""
        start_day  = today + timedelta(days=offset or -today.weekday())
        where = (cls.deal_open >= start_day) & (cls.deal_open <= start_day+timedelta(days=7))
        qs =  (qs or cls.query).filter(where)
        return qs

    @property
    def short_title(self):
        if len(self.title) > 20:
            return u"%s..." % self.title[:20]
        else:
            return self.title

    ## todo implement 
    @property
    def service_info_list(self):
        import warnings
        warnings.warn("this is dummy for serviceIcon")
        return ["icon-fanclub", "icon-crecache"]

    @property
    def ticket_icon_list(self):
        import warnings
        warnings.warn("this is dummy for ticketIcon")
        return ["icon-select", "icon-keep", "icon-official", "icon-goods", "icon-event"]



# class APISingleton(Base):
#     __tablename__ = "apisingleton"
#     id = sa.Column(sa.Integer, primary_key=True)
#     hashed_sha1 = sa.Column(sa.Unicode(length=40))
#     hashed_md5 = sa.Column(sa.Unicode(length=32))

#     created_at = sa.Column(sa.DateTime, default=datetime.now)
#     updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

#     __table_args__ = (
#         sa.UniqueConstraint('hashed_sha1', 'hashed_md5'),
#         )

#     def set_hashed(self, data):
#         string = str(data)
#         self.hashed_sha1 = hashlib.sha1(string).hexdigest
#         self.hashed_md5 = hashlib.md5(string).hexdigest
