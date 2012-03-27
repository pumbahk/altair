from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import CountdownWidget
    from .models import CountdownWidgetResource
    config.add_route("countdown_widget_create", "/widget/countdown/create", factory=CountdownWidgetResource)
    config.add_route("countdown_widget_delete", "/widget/countdown/delete", factory=CountdownWidgetResource)
    config.add_route("countdown_widget_update", "/widget/countdown/update", factory=CountdownWidgetResource)
    config.add_route("countdown_widget_dialog", "/widget/countdown/dialog", factory=CountdownWidgetResource)

    settings = {
        "model": CountdownWidget, 
        "name": CountdownWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
