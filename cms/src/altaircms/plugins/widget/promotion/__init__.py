from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    config.add_widgetname("promotion")
    from .models import PromotionWidget
    config.add_route("promotion_widget_create", "/widget/promotion/create", factory=".models.PromotionWidgetResource")
    config.add_route("promotion_widget_delete", "/widget/promotion/delete", factory=".models.PromotionWidgetResource")
    config.add_route("promotion_widget_update", "/widget/promotion/update", factory=".models.PromotionWidgetResource")
    config.add_route("promotion_widget_dialog", "/widget/promotion/dialog", factory=".models.PromotionWidgetResource")

    settings = {
        "model": PromotionWidget, 
        "name": PromotionWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")

    utility = config.registry.settings.get("altaircms.plugins.promotion.imagefetch.utility")
    if utility:
        config.registry.registerUtility(config.maybe_dotted(utility), 
                                        config.maybe_dotted(".interfaces.IPromotionManager"))
    config.add_route("promotion_slideshow", "/promotion/slideshow")
    config.add_route("api_promotion_main_image", "/promotion/mainimage", factory=".models.PromotionWidgetResource")


