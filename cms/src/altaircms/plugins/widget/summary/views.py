from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from .helpers import _items_from_page
import logging
from altaircms.page.models import Page

@view_defaults(custom_predicates=(require_login,))
class SummaryWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        """ argument data = [items, use_notify]
        """
        page_id = self.request.json_body["page_id"]
        items = self.request.json_body["data"]["items"]
        if self.request.json_body["data"].get("use_notify"):
            bound_event_id = self.request.allowable(Page).filter_by(id=page_id).with_entities("event_id").scalar()
        else:
            bound_event_id = None
        context = self.request.context
        widget = context.get_widget(self.request.json_body.get("pk"))
        widget = context.update_data(widget, page_id=page_id, items=items, bound_event_id=bound_event_id)
        context.add(widget, flush=True)

        r = self.request.json_body.copy()
        r.update(pk=widget.id)
        return r

    @view_config(route_name="summary_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="summary_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="summary_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="summary_widget_dialog", renderer="altaircms.plugins.widget:summary/dialog.mako", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        items = widget.items or "[]"
        return {"widget": widget, "items": items}


@view_config(route_name="api_summary_widget_data_from_db", renderer="json", request_method="GET")
def api_summary_widget_initial_data(context, request):
    page_id = request.GET["page"]
    logging.debug("*api* summary widget items get from db (page_id=%s)" % page_id)
    return _items_from_page(context._get_page(page_id))
