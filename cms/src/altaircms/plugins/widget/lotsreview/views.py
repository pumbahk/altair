from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from . import forms
import logging
from webob.multidict import MultiDict
logger = logging.getLogger(__name__)

@view_defaults(custom_predicates=(require_login,))
class LotsreviewWidgetView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _create_or_update(self):
        try:
            form = forms.LotsreviewForm(MultiDict(self.request.json_body["data"], page_id=self.request.json_body["page_id"]))
            if not form.validate():
                logger.warn(str(form.errors))
                r = self.request.json_body.copy()
                r.update(pk=None)
                return r
            params = form.data
            widget = self.context.get_widget(self.request.json_body.get("pk"))
            widget = self.context.update_data(widget, **params)
            self.context.add(widget, flush=True)

            r = self.request.json_body.copy()
            r.update(pk=widget.id)
        except Exception, e:
            logger.exception(str(e))
            r = self.request.json_body.copy()
            r.update(pk=None)
            return r
        return r


    @view_config(route_name="lotsreview_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="lotsreview_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="lotsreview_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="lotsreview_widget_dialog", renderer="altaircms.plugins.widget:lotsreview/dialog.html", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        params = widget.to_dict()
        params.update(widget.attributes or {})
        form = forms.LotsreviewForm(**params)
        return {"widget": widget, "form": form}

