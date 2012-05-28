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

HEADING_DISPATCH = {
    u"チケットスター：イベント詳細見出し": u'<h2 id="%s">%s</h2>', 
    u"チケットスター：トップページ見出し": u'<h2 id="%s" class="index heading">%s</h2>',  #/static/ticketstar/css/custom.css
    u"チケットスター：スポーツ見出し": u'<h2 id="%s" class="sports heading">%s</h2>',  #/static/ticketstar/css/custom.css
    u"チケットスター：音楽見出し": u'<h2 id="%s" class="music heading">%s</h2>',  #/static/ticketstar/css/custom.css
    u"チケットスター：演劇見出し": u'<h2 id="%s" class="stage heading">%s</h2>',  #/static/ticketstar/css/custom.css
    u"チケットスター：その他見出し": u'<h2 id="%s" class="other heading">%s</h2>',  #/static/ticketstar/css/custom.css
    u"チケットスター：ヘルプページ見出し": u'<h2 id="%s" class="help heading">%s</h2>',  #/static/ticketstar/css/custom.css
    u"チケットスター：公演中止情報ページ見出し":  u'<h2 id="%s" class="change heading">%s</h2>',  #/static/ticketstar/css/custom.css
    u"チケットスター：サイドバー見出し": u'<h2 id="%s" class="sidebar-heading">%s</h2>'
    }
HEADING_KIND_CHOICES = [(x, x) for x in HEADING_DISPATCH]

class HeadingWidget(Widget):
    implements(IWidget)
    type = "heading"

    # template_name = "altaircms.plugins.widget:heading/render.mako"
    __tablename__ = "widget_heading"
    __mapper_args__ = {"polymorphic_identity": type}

    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    kind = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.Unicode(255))

    @property
    def html_id(self):
        return "heading%d" % self.id

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        fmt = HEADING_DISPATCH.get(self.kind)
        if fmt:
            content = fmt % (self.html_id, self.text)
        else:
            content = u"heading widget: kind=%s is not found" % self.kind
        bsettings.add(bname, content)

class HeadingWidgetResource(HandleSessionMixin,
                            UpdateDataMixin,
                            HandleWidgetMixin,
                            RootFactory
                            ):
    WidgetClass = HeadingWidget

    def get_widget(self, widget_id):
        return self._get_or_create(HeadingWidget, widget_id)
