# coding: utf-8

import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession
from datetime import datetime

class Event(BaseOriginalMixin, Base):
    """
    イベント

    @TODO: 席図をくっつける
    """
    __tablename__ = "event"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now())
    updated_at = sa.Column(sa.DateTime, default=datetime.now())

    title = sa.Column(sa.Unicode(255))
    subtitle = sa.Column(sa.Unicode(255), default=u"")
    description = sa.Column(sa.Unicode(255), default=u"")
    place = sa.Column(sa.Unicode(255), default=u"")
    inquiry_for = sa.Column(sa.Unicode(255), default=u"")
    event_open = sa.Column(sa.DateTime)
    event_close = sa.Column(sa.DateTime)
    deal_open = sa.Column(sa.DateTime)
    deal_close = sa.Column(sa.DateTime)

    is_searchable = sa.Column(sa.Integer, default=0)

    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id"))

    @property
    def short_title(self):
        if len(self.title) > 20:
            return u"%s..." % self.title[:20]
        else:
            return self.title

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

