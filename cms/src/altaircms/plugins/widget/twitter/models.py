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

from pyramid.renderers import render

class TwitterWidget(Widget):
    implements(IWidget)
    type = "twitter"

    template_name = "altaircms.plugins.widget:twitter/render.mako"
    __tablename__ = "widget_twitter"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    search_query = sa.Column(sa.Unicode(255), doc=u"検索ワード")
    title = sa.Column(sa.Unicode(255), doc=u"タイトル")
    subject = sa.Column(sa.Unicode(255), doc=u"見出し") ## caption

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")

        content = render(self.template_name, {"widget": self})
        bsettings.add(bname, content)
        
class TwitterWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = TwitterWidget

    def get_widget(self, widget_id):
        return self._get_or_create(TwitterWidget, widget_id)
