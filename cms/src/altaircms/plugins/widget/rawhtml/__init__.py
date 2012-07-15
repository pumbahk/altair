from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import RawhtmlWidget
    from .models import RawhtmlWidgetResource

    config.add_route("rawhtml_widget_create", "/widget/rawhtml/create", factory=RawhtmlWidgetResource)
    config.add_route("rawhtml_widget_delete", "/widget/rawhtml/delete", factory=RawhtmlWidgetResource)
    config.add_route("rawhtml_widget_update", "/widget/rawhtml/update", factory=RawhtmlWidgetResource)
    config.add_route("rawhtml_widget_dialog", "/widget/rawhtml/dialog", factory=RawhtmlWidgetResource)

    settings = {
        "model": RawhtmlWidget, 
        "name": RawhtmlWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
