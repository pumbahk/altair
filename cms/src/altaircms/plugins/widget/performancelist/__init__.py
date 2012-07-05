from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import PerformancelistWidget
    from .models import PerformancelistWidgetResource
    config.add_route("performancelist_widget_create", "/widget/performancelist/create", factory=PerformancelistWidgetResource)
    config.add_route("performancelist_widget_delete", "/widget/performancelist/delete", factory=PerformancelistWidgetResource)
    config.add_route("performancelist_widget_update", "/widget/performancelist/update", factory=PerformancelistWidgetResource)
    config.add_route("performancelist_widget_dialog", "/widget/performancelist/dialog", factory=PerformancelistWidgetResource)

    settings = {
        "model": PerformancelistWidget, 
        "name": PerformancelistWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
