from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import DetailWidget
    from .models import DetailWidgetResource
    config.add_route("detail_widget_create", "/widget/detail/create", factory=DetailWidgetResource)
    config.add_route("detail_widget_delete", "/widget/detail/delete", factory=DetailWidgetResource)
    config.add_route("detail_widget_update", "/widget/detail/update", factory=DetailWidgetResource)
    config.add_route("detail_widget_dialog", "/widget/detail/dialog", factory=DetailWidgetResource)

    settings = {
        "model": DetailWidget, 
        "name": DetailWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
