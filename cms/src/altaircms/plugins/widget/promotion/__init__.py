from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import PromotionWidget
    from .models import PromotionWidgetResource
    config.add_route("promotion_widget_create", "/widget/promotion/create", factory=PromotionWidgetResource)
    config.add_route("promotion_widget_delete", "/widget/promotion/delete", factory=PromotionWidgetResource)
    config.add_route("promotion_widget_update", "/widget/promotion/update", factory=PromotionWidgetResource)
    config.add_route("promotion_widget_dialog", "/widget/promotion/dialog", factory=PromotionWidgetResource)

    settings = {
        "model": PromotionWidget, 
        "name": PromotionWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
