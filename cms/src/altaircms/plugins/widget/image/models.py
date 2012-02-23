from altaircms.interfaces import IWidget
from zope.interface import implements
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base import asset
from altaircms.plugins.base import HandleSessionMixin
from altaircms.plugins.base import UpdateDataMixin

import sqlalchemy as sa
import sqlalchemy.orm as orm

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


class ImageWidgetResource(HandleSessionMixin, UpdateDataMixin):
    from altaircms.asset.models import ImageAsset
    def __init__(self, request):
        self.request = request

    def _get_or_create(self, model, widget_id):
        if widget_id is None:
            return model()
        else:
            return DBSession.query(model).filter(model.id == widget_id).one()
        
    def get_image_widget(self, widget_id):
        return self._get_or_create(ImageWidget, widget_id)

    def get_image_asset_query(self):
        return self.ImageAsset.query

    def get_image_asset(self, asset_id):
        return self.ImageAsset.query.filter(self.ImageAsset.id == asset_id).one()
