from zope.interface import implements
from pyramid.renderers import render
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

from altaircms.lib.interception import not_support_if_keyerror


## todo refactoring
def ticket_icon_merge_settings(widget, bname, bsettings):
    bsettings.need_extra_in_scan("event")

    @not_support_if_keyerror("iconset widget: %(err)s")
    def ticket_icon_render():
        event = bsettings.extra["event"]
        template_name = "altaircms.plugins.widget:iconset/ticket_icon_render.mako"

        icon_classes = event.ticket_icon_list
        return render(template_name, {"icon_classes": icon_classes})
    bsettings.add(bname, ticket_icon_render)

MERGE_SETTINGS_DISPATH = {
    "ticket_icon": ticket_icon_merge_settings
    }

### 

class IconsetWidget(Widget):
    implements(IWidget)
    type = "iconset"

    __tablename__ = "widget_iconset"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    kind = sa.Column(sa.String(length=32), default="ticket_icon", nullable=False)

    def merge_settings(self, bname, bsettings):
        merge_settings_function = MERGE_SETTINGS_DISPATH[self.kind]
        merge_settings_function(self, bname, bsettings)

class IconsetWidgetResource(HandleSessionMixin,
                            UpdateDataMixin,
                            HandleWidgetMixin,
                            RootFactory
                          ):
    WidgetClass = IconsetWidget

    def get_widget(self, widget_id):
        return self._get_or_create(IconsetWidget, widget_id)
