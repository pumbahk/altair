from pyramid.view import view_config, view_defaults
import logging
logger = logging.getLogger(__name__)
from altaircms.auth.api import require_login
from altaircms.auth.api import get_or_404
from altaircms.page.models import Page    
from . import forms

@view_defaults(custom_predicates=(require_login,))
class TopicWidgetView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def _create_or_update(self):
        try:
            data = self.request.json_body["data"]
            data["tag"] = self.context.Tag.query.filter_by(id=data["tag"]).one()
            page_id = self.request.json_body["page_id"]
            widget = self.context.get_widget(self.request.json_body.get("pk"))
            widget = self.context.update_data(widget,
                                         page_id=page_id, 
                                         **data)
            self.context.add(widget, flush=True)
            r = self.request.json_body.copy()
            r.update(pk=widget.id)
        except Exception, e:
            logger.exception(str(e))
        return r

    @view_config(route_name="topic_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="topic_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="topic_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="topic_widget_dialog", renderer="altaircms.plugins.widget:topic/dialog.html", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.GET["page"])
        form = forms.TopicChoiceForm(**widget.to_dict()).configure(self.request, page)
        return {"form": form}
