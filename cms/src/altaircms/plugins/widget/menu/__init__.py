from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import MenuWidget
    from .models import MenuWidgetResource
    config.add_route("menu_widget_create", "/widget/menu/create", factory=MenuWidgetResource)
    config.add_route("menu_widget_delete", "/widget/menu/delete", factory=MenuWidgetResource)
    config.add_route("menu_widget_update", "/widget/menu/update", factory=MenuWidgetResource)
    config.add_route("menu_widget_dialog", "/widget/menu/dialog", factory=MenuWidgetResource)

    settings = {
        "model": MenuWidget, 
        "name": MenuWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
