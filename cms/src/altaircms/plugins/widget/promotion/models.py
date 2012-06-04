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
from altaircms.plugins.base import Base
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
import altaircms.helpers as h

## fixme: rename **info
PromotionInfo = namedtuple("PromotionInfo", "idx thumbnails message main main_link links messages interval_time unit_candidates")

def promotion_merge_settings(template_name, limit, widget, bname, bsettings):
    def slideshow_render():
        request = bsettings.extra["request"]
            ## fixme real implementation
        from . import api
        pm = api.get_promotion_manager(request)
        params = {"show_image": pm.show_image, "info": pm.promotion_info(request, widget.promotion, limit=limit)}
        return render(template_name, params, request=request)

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

class Promotion(Base):
    query = DBSession.query_property()
    __tablename__ = "promotion"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255), index=True)
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))
    site = orm.relationship("Site")

    INTERVAL_TIME = 5000
    def as_info(self, request, idx=0, limit=15):
        ## todo optimize
        punits = self.promotion_units[:limit] if len(self.promotion_units) > limit else self.promotion_units
        selected = punits[idx]
        return PromotionInfo(
            thumbnails=[h.asset.to_show_page(request, pu.thumbnail) for pu in punits], 
            idx=idx, 
            message=selected.text, 
            main=h.asset.to_show_page(request, selected.main_image), 
            main_link=selected.get_link(request), 
            links=[pu.get_link(request) for pu in punits], 
            messages=[pu.text for pu in punits], 
            interval_time = self.INTERVAL_TIME, 
            unit_candidates = [int(pu.id) for pu in punits]
            )

class PromotionUnit(Base):
    query = DBSession.query_property()
    __tablename__ = "promotion_unit"
    id = sa.Column(sa.Integer, primary_key=True)
    promotion_id = sa.Column(sa.Integer, sa.ForeignKey("promotion.id"))
    promotion = orm.relationship("Promotion", backref="promotion_units")
    main_image_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"))
    main_image = orm.relationship("ImageAsset", uselist=False, primaryjoin="PromotionUnit.main_image_id==ImageAsset.id")
    thumbnail_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"))
    thumbnail = orm.relationship("ImageAsset", uselist=False, primaryjoin="PromotionUnit.thumbnail_id==ImageAsset.id")
    text = sa.Column(sa.UnicodeText, default=u"no message")

    ## linkとpagesetは排他的
    link = sa.Column(sa.Unicode(255))
    pageset_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"))
    pageset = orm.relationship("PageSet")

    def validate(self):
        return self.pageset or self.link and not (self.pageset and self.link)

    def get_link(self, request):
        """ promotion枠の画像をクリックし時の飛び先を決める。pageがない場合にはurlを見る"""
        if self.pageset:
            return h.front.to_publish_page_from_pageset(request, self.pageset)
        else:
            return self.link

class PromotionWidget(Widget):
    implements(IWidget)
    type = "promotion"

    __tablename__ = "widget_promotion"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    promotion_id = sa.Column(sa.Integer, sa.ForeignKey("promotion.id"))
    promotion = orm.relationship("Promotion", uselist=False)
    kind = sa.Column(sa.Unicode(length=255))

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        return PROMOTION_DISPATH[self.kind](self, bname, bsettings)

class PromotionWidgetResource(HandleSessionMixin,
                              UpdateDataMixin,
                              HandleWidgetMixin,
                              RootFactory
                              ):
    WidgetClass = PromotionWidget
    PromotionUnit = PromotionUnit
    Promotion = Promotion

    def get_widget(self, widget_id):
        return self._get_or_create(PromotionWidget, widget_id)
