from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import IconsetWidget
    from .models import IconsetWidgetResource
    config.add_route("iconset_widget_create", "/widget/iconset/create", factory=IconsetWidgetResource)
    config.add_route("iconset_widget_delete", "/widget/iconset/delete", factory=IconsetWidgetResource)
    config.add_route("iconset_widget_update", "/widget/iconset/update", factory=IconsetWidgetResource)
    config.add_route("iconset_widget_dialog", "/widget/iconset/dialog", factory=IconsetWidgetResource)

    settings = {
        "model": IconsetWidget, 
        "name": IconsetWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
