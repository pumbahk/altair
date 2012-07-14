# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

class RawhtmlWidget(Widget):
    implements(IWidget)
    type = "rawhtml"

    template_name = "altaircms.plugins.widget:rawhtml/render.mako"
    __tablename__ = "widget_rawhtml"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    text = sa.Column(sa.UnicodeText, default=u"")

    def merge_settings(self, bname, bsettings):
        bsettings.add(bname, self.text)

class RawhtmlWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = RawhtmlWidget

    def get_widget(self, widget_id):
        return self._get_or_create(RawhtmlWidget, widget_id)
