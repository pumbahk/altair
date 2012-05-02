# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget
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

"""
kindをもとに絞り込みを行う予定。
"""

## fixme: rename **info
PromotionInfo = namedtuple("PromotionInfo", "idx thumnails message main link")

class Promotion(Base):
    __tablename__ = "promotion"
    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    name = sa.Column(sa.Unicode(255), index=True)
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))
    site = orm.relationship("Site")

    def as_info(self, idx=0, limit=15):
        punits = self.promotion_units
        selected = punits[idx]
        return PromotionInfo(
            idx=idx, 
            thumnails=[pu.thunmnails for pu in punits], 
            message=selected.text, 
            link=selected.link, 
            main=selected.main_image
            )

class PromotionUnit(Base):
    __tablename__ = "promotion_unit"
    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    promotion_id = sa.Column(sa.Integer, sa.ForeignKey("promotion.id"))
    promotion = orm.relationship("Promotion", backref="promotion_units")
    main_image_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"))
    main_image = orm.relationship("ImageAsset", uselist=False, primaryjoin="PromotionUnit.main_image_id==ImageAsset.id")
    thumbnail_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"))
    thumbnail = orm.relationship("ImageAsset", uselist=False, primaryjoin="PromotionUnit.thumbnail_id==ImageAsset.id")
    link = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.UnicodeText, default=u"no message")

class PromotionWidget(Widget):
    implements(IWidget)
    type = "promotion"

    template_name = "altaircms.plugins.widget:promotion/render.mako"
    __tablename__ = "widget_promotion"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    promotion_id = sa.Column(sa.Integer, sa.ForeignKey("promotion.id"))
    promotion = orm.relationship("Promotion", uselist=False)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        def slideshow_render():
            request = bsettings.extra["request"]
            return render(self.template, {"info":self.as_info()}, request=request)
        bsettings.add(bname, slideshow_render)

class PromotionWidgetResource(HandleSessionMixin,
                              UpdateDataMixin,
                              HandleWidgetMixin,
                              RootFactory
                              ):
    WidgetClass = PromotionWidget

    def get_widget(self, widget_id):
        return self._get_or_create(PromotionWidget, widget_id)
