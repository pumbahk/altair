# coding: utf-8
from sqlalchemy.sql.expression import desc

from altaircms.models import DBSession
from altaircms.widget.models import Widget
from altaircms.widget.mappers import *
from altaircms.asset.models import *

def widget_convert_to_dict(widget):
    cls = globals()[widget.type.capitalize() + 'WidgetMapper'](widget)
    return {widget.type: cls.as_dict()}

def get_widget_list(site_id=None):
    objects = DBSession.query(Widget).order_by(desc(Widget.id)).all()
    return objects

from .api.resources import WidgetResource

def includeme(config):
    config.add_route("structure_create", "/api/structure/create", factory=WidgetResource)
    config.add_route("structure_update", "/api/structure/update", factory=WidgetResource)
    config.add_route("structure_get", "/api/structure/get", factory=WidgetResource)

    config.add_route("image_widget_create", "/api/widget/image_widget/create", factory=WidgetResource)
    config.add_route("image_widget_update", "/api/widget/image_widget/update", factory=WidgetResource)
    config.add_route("image_widget_delete", "/api/widget/image_widget/delete", factory=WidgetResource)
    config.add_route("image_widget_dialog", "/api/widget/image_widget/dialog", factory=WidgetResource)

    config.add_route("freetext_widget_create", "/api/widget/freetext_widget/create", factory=WidgetResource)
    config.add_route("freetext_widget_update", "/api/widget/freetext_widget/update", factory=WidgetResource)
    config.add_route("freetext_widget_delete", "/api/widget/freetext_widget/delete", factory=WidgetResource)
    config.add_route("freetext_widget_dialog", "/api/widget/freetext_widget/dialog", factory=WidgetResource)
