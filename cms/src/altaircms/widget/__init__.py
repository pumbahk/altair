# coding: utf-8
from .api.resources import WidgetResource

def includeme(config):
    config.add_route("structure_create", "/api/structure/create", factory=WidgetResource)
    config.add_route("structure_update", "/api/structure/update", factory=WidgetResource)
    config.add_route("structure_get", "/api/structure/get", factory=WidgetResource)
