from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    config.add_widgetname("reuse")
    from .models import ReuseWidget
    from .models import ReuseWidgetResource
    config.add_route("reuse_widget_create", "/widget/reuse/create", factory=ReuseWidgetResource)
    config.add_route("reuse_widget_delete", "/widget/reuse/delete", factory=ReuseWidgetResource)
    config.add_route("reuse_widget_update", "/widget/reuse/update", factory=ReuseWidgetResource)
    config.add_route("reuse_widget_dialog", "/widget/reuse/dialog", factory=ReuseWidgetResource)
    config.add_view(name="reuse_redering_source_page_only", view="altaircms.plugins.widget.reuse.views.rendering_source_page")
    settings = {
        "model": ReuseWidget, 
        "name": ReuseWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")

