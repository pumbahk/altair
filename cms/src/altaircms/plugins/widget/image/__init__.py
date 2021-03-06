from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    config.add_widgetname("image")
    from .models import ImageWidget
    from .resources import ImageWidgetResource
    config.add_route("image_widget_create", "/widget/image/create", factory=ImageWidgetResource)
    config.add_route("image_widget_delete", "/widget/image/delete", factory=ImageWidgetResource)
    config.add_route("image_widget_update", "/widget/image/update", factory=ImageWidgetResource)
    config.add_route("image_widget_dialog", "/widget/image/dialog", factory=ImageWidgetResource)
    config.add_route("image_widget_search", "/widget/image/search", factory=ImageWidgetResource)
    config.add_route("image_widget_search_first", "/widget/image/search/first", factory=ImageWidgetResource)
    config.add_route("image_widget_fetch", "/widget/image/fetch", factory=ImageWidgetResource)
    config.add_route("image_widget_tag_search", "/widget/image/tagsearch", factory=ImageWidgetResource)
    config.add_route("image_widget_tag_search_first", "/widget/image/tagsearch/first", factory=ImageWidgetResource)
    settings = {
        "model": ImageWidget, 
        "name": ImageWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
