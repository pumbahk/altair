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
MovieAsset = asset.models.MovieAsset

class MovieWidget(Widget):
    implements(IWidget)
    type = "movie"

    template_name = "altaircms.plugins.widget:movie/render.mako"
    __tablename__ = "widget_movie"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    asset_id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"))
    asset = orm.relationship(MovieAsset, backref="widget", uselist=False)

    def __init__(self, id=None, asset_id=None):
        self.id = id
        self.asset_id = asset_id

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        def movie_render():
            return render(self.template_name,
                          {"widget": self,
                           "request": bsettings.extra["request"]})
        bsettings.add(bname, movie_render)

class MovieWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          AssetWidgetResourceMixin, 
                          RootFactory
                          ):
    WidgetClass = MovieWidget
    AssetClass = MovieAsset

