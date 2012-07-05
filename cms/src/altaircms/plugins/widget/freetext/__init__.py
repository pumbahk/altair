from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import FreetextWidget
    from .models import FreetextWidgetResource
    config.add_route("freetext_widget_create", "/widget/freetext/create", factory=FreetextWidgetResource)
    config.add_route("freetext_widget_delete", "/widget/freetext/delete", factory=FreetextWidgetResource)
    config.add_route("freetext_widget_update", "/widget/freetext/update", factory=FreetextWidgetResource)
    config.add_route("freetext_widget_dialog", "/widget/freetext/dialog", factory=FreetextWidgetResource)

    settings = {
        "model": FreetextWidget, 
        "name": FreetextWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
