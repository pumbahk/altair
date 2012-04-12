# coding: utf-8
from .api.resources import WidgetResource

def includeme(config):
    config.add_route('widget', '/widget/{widget_id}')
    config.add_route('widget_add', '/widget/form/{widget_type}')
    config.add_route('widget_delete', '/widget/{widget_id}/delete')
    config.add_route('widget_list', '/widget/')

    ## api
    config.add_route("structure_create", "/api/structure/create", factory=WidgetResource)
    config.add_route("structure_update", "/api/structure/update", factory=WidgetResource)
    config.add_route("structure_get", "/api/structure/get", factory=WidgetResource)
    config.scan(".")
