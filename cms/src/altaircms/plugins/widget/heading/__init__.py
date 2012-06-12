from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import HeadingWidget
    from .models import HeadingWidgetResource
    config.add_route("heading_widget_create", "/widget/heading/create", factory=HeadingWidgetResource)
    config.add_route("heading_widget_delete", "/widget/heading/delete", factory=HeadingWidgetResource)
    config.add_route("heading_widget_update", "/widget/heading/update", factory=HeadingWidgetResource)
    config.add_route("heading_widget_dialog", "/widget/heading/dialog", factory=HeadingWidgetResource)

    config.add_route("api_heading_title", "/widget/heading/api/title", factory=HeadingWidgetResource)

    settings = {
        "model": HeadingWidget, 
        "name": HeadingWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
