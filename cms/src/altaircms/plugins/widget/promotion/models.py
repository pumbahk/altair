# -*- coding:utf-8 -*-
from zope.interface import implements
from altaircms.interfaces import IWidget
import functools
from collections import namedtuple
import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.renderers import render

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
import altaircms.helpers as h
from altaircms.topic.models import Kind
from altaircms.topic.models import Promotion

## fixme: rename **info
PromotionInfo = namedtuple("PromotionInfo", "idx thumbnails message main main_link links messages interval_time unit_candidates")

def promotion_merge_settings(template_name, limit, widget, bname, bsettings):
    def slideshow_render():
        request = bsettings.extra["request"]
        from . import api
        pm = api.get_promotion_manager(request)
        info = pm.promotion_info(request, widget.promotion_sheet, limit=limit)
        if info:
            params = {"show_image": pm.show_image, "info": info}
            return render(template_name, params, request=request)
        else:
            return u''

    bsettings.add(bname, slideshow_render)


PROMOTION_DISPATH = {
    u"チケットスター:Topプロモーション枠": functools.partial(
        promotion_merge_settings, 
        "altaircms.plugins.widget:promotion/render.mako", 15, 
        ), 
    u"チケットスター:カテゴリTopプロモーション枠":
        functools.partial(
        promotion_merge_settings, 
        "altaircms.plugins.widget:promotion/category_render.mako", 4, 
        )
    }

class PromotionSheet(object):
    INTERVAL_TIME = 5000

    def __init__(self, promotion_units):
        self.promotion_units = promotion_units

    def as_info(self, request, idx=0, limit=15):
        ## todo optimize
        punits = self.promotion_units[:limit] if len(self.promotion_units) > limit else self.promotion_units
        if not punits:
            return None

        selected = punits[idx]
        return PromotionInfo(
            thumbnails=[h.asset.to_show_page(request, pu.thumbnail) for pu in punits], 
            idx=idx, 
            message=selected.text, 
            main=h.asset.to_show_page(request, selected.main_image), 
            main_link=h.link.get_link_from_promotion(request, selected), 
            links=[h.link.get_link_from_promotion(request, pu) for pu in punits], 
            messages=[pu.text for pu in punits], 
            interval_time = self.INTERVAL_TIME, 
            unit_candidates = [int(pu.id) for pu in punits]
            )

class PromotionWidget(Widget):
    implements(IWidget)
    type = "promotion"

    __tablename__ = "widget_promotion"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    display_type = sa.Column(sa.Unicode(length=255))
    kind_id = sa.Column(sa.Integer, sa.ForeignKey("kind.id"))
    kind = orm.relationship("Kind", uselist=False)

    @property
    def promotion_sheet(self, d=None):
        from altaircms.topic.models import Promotion
        qs = Promotion.matched_qs(d=d, kind=self.kind.name).options(orm.joinedload("thumbnail"), orm.joinedload("linked_page"))
        return PromotionSheet(qs.all()) ##

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        display_type = self.display_type or u"チケットスター:カテゴリTopプロモーション枠" #ugly
        return PROMOTION_DISPATH[display_type](self, bname, bsettings) 

class PromotionWidgetResource(HandleSessionMixin,
                              UpdateDataMixin,
                              HandleWidgetMixin,
                              RootFactory
                              ):
    Promotion = Promotion
    WidgetClass = PromotionWidget
    Kind = Kind
    def get_widget(self, widget_id):
        return self._get_or_create(PromotionWidget, widget_id)
