from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    config.add_widgetname("flash")
    from .models import FlashWidget
    from .models import FlashWidgetResource
    config.add_route("flash_widget_create", "/widget/flash/create", factory=FlashWidgetResource)
    config.add_route("flash_widget_delete", "/widget/flash/delete", factory=FlashWidgetResource)
    config.add_route("flash_widget_update", "/widget/flash/update", factory=FlashWidgetResource)
    config.add_route("flash_widget_dialog", "/widget/flash/dialog", factory=FlashWidgetResource)

    settings = {
        "model": FlashWidget, 
        "name": FlashWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
