from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import TopicWidget
    from .models import TopicWidgetResource
    config.add_route("topic_widget_create", "/widget/topic/create", factory=TopicWidgetResource)
    config.add_route("topic_widget_delete", "/widget/topic/delete", factory=TopicWidgetResource)
    config.add_route("topic_widget_update", "/widget/topic/update", factory=TopicWidgetResource)
    config.add_route("topic_widget_dialog", "/widget/topic/dialog", factory=TopicWidgetResource)

    # config.add_route("topic_widget_dialog_form", "/widget/topic/dialog/api/form", factory=TopicWidgetResource)
    settings = {
        "model": TopicWidget, 
        "name": TopicWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
