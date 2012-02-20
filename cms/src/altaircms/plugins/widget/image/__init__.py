from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import ImageWidget
    from .models import ImageWidgetResource
    config.add_route("image_widget_create", "/widget/image/create", factory=ImageWidgetResource)
    config.add_route("image_widget_delete", "/widget/image/delete", factory=ImageWidgetResource)
    config.add_route("image_widget_update", "/widget/image/update", factory=ImageWidgetResource)
    config.add_route("image_widget_dialog", "/widget/image/dialog", factory=ImageWidgetResource)

    settings = {
        "model": ImageWidget, 
        "name": ImageWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js")
        }
    widget_plugin_install(config, settings)
