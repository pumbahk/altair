from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import SummaryWidget
    from .models import SummaryWidgetResource
    config.add_route("summary_widget_create", "/widget/summary/create", factory=SummaryWidgetResource)
    config.add_route("summary_widget_delete", "/widget/summary/delete", factory=SummaryWidgetResource)
    config.add_route("summary_widget_update", "/widget/summary/update", factory=SummaryWidgetResource)
    config.add_route("summary_widget_dialog", "/widget/summary/dialog", factory=SummaryWidgetResource)

    settings = {
        "model": SummaryWidget, 
        "name": SummaryWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
