from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import AnchorlistWidget
    from .models import AnchorlistWidgetResource
    config.add_route("anchorlist_widget_create", "/widget/anchorlist/create", factory=AnchorlistWidgetResource)
    config.add_route("anchorlist_widget_delete", "/widget/anchorlist/delete", factory=AnchorlistWidgetResource)
    config.add_route("anchorlist_widget_update", "/widget/anchorlist/update", factory=AnchorlistWidgetResource)
    config.add_route("anchorlist_widget_dialog", "/widget/anchorlist/dialog", factory=AnchorlistWidgetResource)

    settings = {
        "model": AnchorlistWidget, 
        "name": AnchorlistWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
