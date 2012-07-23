from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    config.add_widgetname("ticketlist")
    from .models import TicketlistWidget
    from .models import TicketlistWidgetResource
    config.add_route("ticketlist_widget_create", "/widget/ticketlist/create", factory=TicketlistWidgetResource)
    config.add_route("ticketlist_widget_delete", "/widget/ticketlist/delete", factory=TicketlistWidgetResource)
    config.add_route("ticketlist_widget_update", "/widget/ticketlist/update", factory=TicketlistWidgetResource)
    config.add_route("ticketlist_widget_dialog", "/widget/ticketlist/dialog", factory=TicketlistWidgetResource)

    settings = {
        "model": TicketlistWidget, 
        "name": TicketlistWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
