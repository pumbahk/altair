from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import BreadcrumbsWidget
    from .models import BreadcrumbsWidgetResource
    config.add_route("breadcrumbs_widget_create", "/widget/breadcrumbs/create", factory=BreadcrumbsWidgetResource)
    config.add_route("breadcrumbs_widget_delete", "/widget/breadcrumbs/delete", factory=BreadcrumbsWidgetResource)
    config.add_route("breadcrumbs_widget_update", "/widget/breadcrumbs/update", factory=BreadcrumbsWidgetResource)
    config.add_route("breadcrumbs_widget_dialog", "/widget/breadcrumbs/dialog", factory=BreadcrumbsWidgetResource)

    settings = {
        "model": BreadcrumbsWidget, 
        "name": BreadcrumbsWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
