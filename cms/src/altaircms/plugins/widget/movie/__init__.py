from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import MovieWidget
    from .models import MovieWidgetResource
    config.add_route("movie_widget_create", "/widget/movie/create", factory=MovieWidgetResource)
    config.add_route("movie_widget_delete", "/widget/movie/delete", factory=MovieWidgetResource)
    config.add_route("movie_widget_update", "/widget/movie/update", factory=MovieWidgetResource)
    config.add_route("movie_widget_dialog", "/widget/movie/dialog", factory=MovieWidgetResource)

    settings = {
        "model": MovieWidget, 
        "name": MovieWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
