from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import TwitterWidget
    from .models import TwitterWidgetResource
    config.add_route("twitter_widget_create", "/widget/twitter/create", factory=TwitterWidgetResource)
    config.add_route("twitter_widget_delete", "/widget/twitter/delete", factory=TwitterWidgetResource)
    config.add_route("twitter_widget_update", "/widget/twitter/update", factory=TwitterWidgetResource)
    config.add_route("twitter_widget_dialog", "/widget/twitter/dialog", factory=TwitterWidgetResource)

    settings = {
        "model": TwitterWidget, 
        "name": TwitterWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
