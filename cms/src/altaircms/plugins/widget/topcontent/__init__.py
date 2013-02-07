from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    config.add_widgetname("topcontent")
    from .models import TopcontentWidget
    from .models import TopcontentWidgetResource
    config.add_route("topcontent_widget_create", "/widget/topcontent/create", factory=TopcontentWidgetResource)
    config.add_route("topcontent_widget_delete", "/widget/topcontent/delete", factory=TopcontentWidgetResource)
    config.add_route("topcontent_widget_update", "/widget/topcontent/update", factory=TopcontentWidgetResource)
    config.add_route("topcontent_widget_dialog", "/widget/topcontent/dialog", factory=TopcontentWidgetResource)

    # config.add_route("topcontent_widget_dialog_form", "/widget/topcontent/dialog/api/form", factory=TopcontentWidgetResource)
    settings = {
        "model": TopcontentWidget, 
        "name": TopcontentWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
    config.add_has_widget_pages_finder(".api.get_topcontent_widget_pages", name="topcontent")
