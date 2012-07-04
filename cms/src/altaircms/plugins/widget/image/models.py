from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.widget.models import AssetWidgetResourceMixin
from altaircms.plugins.base import DBSession
from altaircms.plugins.base import asset
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

from pyramid.renderers import render
ImageAsset = asset.ImageAsset

class ImageWidget(Widget):
    implements(IWidget)
    type = "image"

    template_name = "altaircms.plugins.widget:image/render.mako"
    __tablename__ = "widget_image"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    href = sa.Column(sa.String(255))
    width = sa.Column(sa.Integer)
    height = sa.Column(sa.Integer)
    alt = sa.Column(sa.Unicode(255))
    asset_id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"))
    asset = orm.relationship(ImageAsset, backref="widget", uselist=False)
    nowrap = sa.Column(sa.Boolean, default=False)

    def __init__(self, id=None, asset_id=None):
        self.id = id
        self.asset_id = asset_id

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        content = lambda : render(self.template_name,
                                  {"widget": self,
                                   "request": bsettings.extra["request"]})
        bsettings.add(bname, content)

class ImageWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          AssetWidgetResourceMixin, 
                          RootFactory
                          ):
    WidgetClass = ImageWidget
    AssetClass = ImageAsset

