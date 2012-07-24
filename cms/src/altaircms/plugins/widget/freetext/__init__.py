# -*- coding:utf-8 -*-
from altaircms.plugins.widget import widget_plugin_install

import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

class AfterInput(Exception):
    def __init__(self, form=None, context=None):
        self.form = form
        self.context = context

def includeme(config):
    config.add_widgetname("freetext")
    from .models import FreetextWidget
    from .models import FreetextWidgetResource
    config.add_route("freetext_widget_create", "/widget/freetext/create", factory=FreetextWidgetResource)
    config.add_route("freetext_widget_delete", "/widget/freetext/delete", factory=FreetextWidgetResource)
    config.add_route("freetext_widget_update", "/widget/freetext/update", factory=FreetextWidgetResource)
    config.add_route("freetext_widget_dialog", "/widget/freetext/dialog", factory=FreetextWidgetResource)

    factory = config.add_crud("freetext_default", 
                              title=u"定型文", 
                              bind_actions=["delete", "update", "list", "create"], 
                              form=".forms.FreetextBodyForm", 
                              model=".models.FreetextDefaultBody", 
                              has_auto_generated_permission=False, permission="authenticated", 
                              after_input_context=AfterInput, 
                              mapper=".mappers.freetext_body_mapper")
    ## overwriten view
    config.add_view("altaircms.lib.crud.views.CreateView", 
                    context=AfterInput, 
                    attr="_after_input", route_name=factory._join("create"), 
                    decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
                    renderer="altaircms.plugins.widget.freetext:subtemplates/default_text_create_input.mako")
    config.add_view("altaircms.lib.crud.views.UpdateView", 
                    context=AfterInput, 
                    attr="_after_input", route_name=factory._join("update"), 
                    decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
                    renderer="altaircms.plugins.widget.freetext:subtemplates/default_text_update_input.mako")

    config.add_route("api_get_default_text", "/widget/freetext/api/default_text")

    settings = {
        "model": FreetextWidget, 
        "name": FreetextWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
