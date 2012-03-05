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

ImageAsset = asset.models.ImageAsset

class ImageWidget(Widget):
    implements(IWidget)
    type = "image"

    template_name = "altaircms.plugins.widget:image/render.mako"
    __tablename__ = "widget_image"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    asset_id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"))
    asset = orm.relationship(ImageAsset, backref="widget", uselist=False)

    def __init__(self, id=None, asset_id=None):
        self.id = id
        self.asset_id = asset_id

class ImageWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          AssetWidgetResourceMixin, 
                          RootFactory
                          ):
    WidgetClass = ImageWidget
    AssetClass = ImageAsset


