from zope.interface import implements
from altaircms.interfaces import IWidget
from markupsafe import Markup
from altaircms.formhelpers import AlignChoiceField
import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.plugins.widget.api import safe_execute
from altaircms.widget.models import Widget
from altaircms.widget.models import AssetWidgetResourceMixin
from altaircms.plugins.base import DBSession
from altaircms.plugins.base import asset
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

from pyramid.renderers import render
ImageAsset = asset.ImageAsset

from altaircms.modellib import MutationDict, JSONEncodedDict

class ImageWidget(Widget):
    implements(IWidget)
    type = "image"

    template_name = "altaircms.plugins.widget:image/render.html"
    __tablename__ = "widget_image"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    href = sa.Column(sa.String(255))
    width = sa.Column(sa.Integer)
    height = sa.Column(sa.Integer)
    alt = sa.Column(sa.Unicode(255))
    asset_id = sa.Column(sa.Integer, sa.ForeignKey("asset.id", ondelete="SET NULL"))
    asset = orm.relationship(ImageAsset, backref="widget", uselist=False)
    nowrap = sa.Column(sa.Boolean, default=False)
    attributes = sa.Column(MutationDict.as_mutable(JSONEncodedDict(255)))

    def __init__(self, id=None, asset_id=None):
        self.id = id
        self.asset_id = asset_id

    @property
    def html_attributes(self):
        attributes = {}
        if self.width:
            attributes["width"] = self.width
        if self.height:
            attributes["height"] = self.height
        if self.alt:
            attributes["alt"] = self.alt
        if self.attributes:
            attributes.update(self.attributes)
        return u" ".join([u'%s="%s"' % (k, v) for k, v in attributes.items()])

    @property
    def html_suffix(self):
        if self.attributes:
            return Markup(AlignChoiceField.convert_as_html_suffix(self.attributes.get("data-align")))
        return ""

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        @safe_execute("image")
        def renderHTML():
            return render(self.template_name,
                   {"widget": self,
                    "request": bsettings.extra["request"]})
        bsettings.add(bname, renderHTML)

class ImageWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          AssetWidgetResourceMixin, 
                          RootFactory
                          ):
    WidgetClass = ImageWidget
    AssetClass = ImageAsset

    def search_asset(self, search_word):
        return self.request.allowable(self.AssetClass).filter(self.AssetClass.title.like("%" + search_word + "%"))
