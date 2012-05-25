from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import PurchaseWidget
    from .models import PurchaseWidgetResource
    config.add_route("purchase_widget_create", "/widget/purchase/create", factory=PurchaseWidgetResource)
    config.add_route("purchase_widget_delete", "/widget/purchase/delete", factory=PurchaseWidgetResource)
    config.add_route("purchase_widget_update", "/widget/purchase/update", factory=PurchaseWidgetResource)
    config.add_route("purchase_widget_dialog", "/widget/purchase/dialog", factory=PurchaseWidgetResource)

    settings = {
        "model": PurchaseWidget, 
        "name": PurchaseWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
