# coding: utf-8

import sqlalchemy as sa
from pyramid.decorator import reify
import sqlalchemy.orm as orm
from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import WithOrganizationMixin
from altaircms.models import DBSession
from altaircms.models import Word, Event_Word
from altaircms.auth.models import Organization
from datetime import datetime
from datetime import timedelta


class Event(BaseOriginalMixin, WithOrganizationMixin, Base):
    """
    イベント

    @TODO: 席図をくっつける
    """
    __tablename__ = "event"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    backend_id = sa.Column(sa.Integer)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    title = sa.Column(sa.Unicode(255))
    subtitle = sa.Column(sa.Unicode(255), default=u"")
    description = sa.Column(sa.Unicode(255), default=u"")
    event_open = sa.Column(sa.DateTime, default=datetime.now)
    event_close = sa.Column(sa.DateTime, default=datetime.now)
    deal_open = sa.Column(sa.DateTime, default=datetime.now)
    deal_close = sa.Column(sa.DateTime, default=datetime.now)
    is_searchable = sa.Column(sa.Boolean, default=True)

    performers = sa.Column(sa.UnicodeText, doc=u"公演者")
    inquiry_for = sa.Column(sa.UnicodeText, default=u"", doc=u"お問い合わせ先")
    notice = sa.Column(sa.UnicodeText, doc=u"注意事項")
    ticket_pickup = sa.Column(sa.UnicodeText, doc=u"チケット引き取り方法")
    ticket_payment = sa.Column(sa.UnicodeText, doc=u"支払い方法")
    code = sa.Column(sa.String(12), doc=u"event code (backend)")
    in_preparation = sa.Column(sa.Boolean, default=False)

    keywords = orm.relationship("Word", backref="events", secondary=Event_Word.__tablename__)

    @reify
    def organization(self):
        return Organization.query.filter_by(id=self.organization_id).one()

    @classmethod
    def near_the_deal_close_query(cls, now, N=7, qs=None):
        """ 現在から販売終了N日前までのqueryを返す"""
        today = datetime(now.year, now.month, now.day)
        limit_day = today + timedelta(days=N)
        where = (cls.deal_open <= now) & (now <= cls.deal_close) & (cls.deal_close <= limit_day)
        return (qs or cls.query).filter(where)

    @classmethod
    def deal_start_this_week_query(cls, now, offset=None, qs=None):
        """今週販売開始するquery(月曜日を週のはじめとする)"""
        today = datetime(now.year, now.month, now.day)
        start_day  = today + timedelta(days=offset or -today.weekday())
        where = (cls.deal_open >= start_day) & (cls.deal_open < start_day+timedelta(days=7)) & ((cls.deal_close == None) | (now <= cls.deal_close))
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
