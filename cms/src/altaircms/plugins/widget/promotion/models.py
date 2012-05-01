# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base import Base
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

"""
まだ、alembicのmigration code書いていない
kindをもとに絞り込みを行う予定。
"""

class Promotion(Base):
    __tablename__ = "promotion"
    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    kind = sa.Column(sa.Unicode(255))
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))
    site = orm.relationship("Site")

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
    kind = sa.Column(sa.Unicode(255))

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        # bsettings.add(bname, "content")

class PromotionWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = PromotionWidget

    def get_widget(self, widget_id):
        return self._get_or_create(PromotionWidget, widget_id)
