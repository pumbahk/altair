# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from zope.interface import implements
from altaircms.interfaces import IWidget
from collections import namedtuple
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
import altaircms.helpers as h
from altaircms.topic.models import PromotionTag
from altaircms.topic.models import Promotion

from altaircms.plugins.widget.api import get_rendering_function_via_page

class PromotionWidget(Widget):
    implements(IWidget)
    type = "promotion"

    __tablename__ = "widget_promotion"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    display_type = sa.Column(sa.Unicode(length=255))
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("topiccoretag.id"))
    tag = orm.relationship("PromotionTag", uselist=False)

    @property
    def promotion_sheet(self, d=None):
        from altaircms.topic.models import Promotion
        qs = Promotion.matched_qs(d=d, tag=self.tag.label).options(orm.joinedload("main_image"), orm.joinedload("linked_page"))
        return PromotionSheet(qs.all()) ##

    def merge_settings(self, bname, bsettings):
        closure = get_rendering_function_via_page(self, bname, bsettings, self.type)
        bsettings.add(bname, closure)

## fixme: rename **info
PromotionInfo = namedtuple("PromotionInfo", "idx thumbnails message main main_link links messages interval_time unit_candidates")

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
            thumbnails=[h.asset.to_show_page(request, pu.main_image, filepath=pu.main_image.thumbnail_path) for pu in punits], 
            idx=idx, 
            message=selected.text, 
            main=h.asset.to_show_page(request, selected.main_image), 
            main_link=h.link.get_link_from_promotion(request, selected), 
            links=[h.link.get_link_from_promotion(request, pu) for pu in punits], 
            messages=[pu.text for pu in punits], 
            interval_time = self.INTERVAL_TIME, 
            unit_candidates = [int(pu.id) for pu in punits]
            )

class PromotionWidgetResource(HandleSessionMixin,
                              UpdateDataMixin,
                              HandleWidgetMixin,
                              RootFactory
                              ):
    Promotion = Promotion
    WidgetClass = PromotionWidget
    Tag = PromotionTag
    def get_widget(self, widget_id):
        return self._get_or_create(PromotionWidget, widget_id)
