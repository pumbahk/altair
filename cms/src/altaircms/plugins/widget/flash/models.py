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

FlashAsset = asset.FlashAsset
from pyramid.renderers import render

class FlashWidget(Widget):
    implements(IWidget)
    type = "flash"

    template_name = "altaircms.plugins.widget:flash/render.mako"
    __tablename__ = "widget_flash"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    asset_id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"))
    asset = orm.relationship(FlashAsset, backref="widget", uselist=False)
    href = sa.Column(sa.String(255))
    width = sa.Column(sa.Integer)
    height = sa.Column(sa.Integer)
    alt = sa.Column(sa.Unicode(255))

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

        if not bsettings.is_attached(self, "js_prerender"):
            bsettings.add("js_prerender", JS_PRERENDER)
            bsettings.attach_widget(self, "js_prerender")

        ## in jquery.ready()
        if not bsettings.is_attached(self, "js_postrender"):
            bsettings.add("js_postrender", JS_POSTRENDER)
            bsettings.attach_widget(self, "js_postrender")

JS_PRERENDER = """\
<script type="text/javascript" src="/static/swfobject.js"></script>
"""

JS_POSTRENDER = """\
    $(".flash-widget").each(function(i,e){
        var flashvars = {};
        var params = {};
        var attributes = {};

        var e = $(e);
        var width = e.attr("width");
        var height = e.attr("height");
        var url = e.attr("url");
        var uid = String(Math.random()); //slack-off
        e.attr("id", uid)
        swfobject.embedSWF(
            url,
            uid, 
            width,
            height, 
            "9.0.0",
            "/static/expressInstall.swf",
            flashvars,
            params,
            attributes
        );
    });
"""


class FlashWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          AssetWidgetResourceMixin, 
                          RootFactory):
    WidgetClass = FlashWidget
    AssetClass = FlashAsset
