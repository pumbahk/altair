# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
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
    tag = orm.relationship("PromotionTag", uselist=False, primaryjoin="PromotionWidget.tag_id==PromotionTag.id")
    system_tag_id = sa.Column(sa.Integer, sa.ForeignKey("topiccoretag.id", ondelete="SET NULL"))
    system_tag = orm.relationship("PromotionTag", uselist=False, primaryjoin="PromotionWidget.system_tag_id==PromotionTag.id")

    def merge_settings(self, bname, bsettings):
        closure = get_rendering_function_via_page(self, bname, bsettings, self.type)
        bsettings.add(bname, closure)



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
