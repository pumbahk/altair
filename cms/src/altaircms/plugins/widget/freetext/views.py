from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from altaircms.auth.api import get_or_404
from . import models
from . import forms

@view_defaults(custom_predicates=(require_login,))
class FreetextWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        freetext = self.request.json_body["data"]["freetext"]
        page_id = self.request.json_body["page_id"]
        context = self.request.context
        widget = context.get_widget(self.request.json_body.get("pk"))
        widget = context.update_data(widget, text=freetext, page_id=page_id)
        context.add(widget, flush=True)

        r = self.request.json_body.copy()
        r.update(pk=widget.id)
        return r

    @view_config(route_name="freetext_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="freetext_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="freetext_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}


    ##
    @view_config(route_name="freetext_widget_dialog", renderer="altaircms.plugins.widget:freetext/dialog.mako", request_method="GET")
    def dialog(self):
        context = self.request.context
        pk = self.request.GET.get("pk")
        widget = context.get_widget(pk)
        choice_form = forms.FreeTextChoiceForm()
        return {"widget": widget, "choice_form": choice_form}
    
    @view_config(route_name="api_get_default_text", request_method="GET", renderer="json", request_param="default_body_id")
    def get_data(self):
        params = self.request.GET
        obj = get_or_404(self.request.allowable(models.FreetextDefaultBody),
                         models.FreetextDefaultBody.id==params.get("default_body_id"))
        return {
            "name": obj.__class__.__name__, 
            "data": {
                "name": obj.name, 
                "text": obj.text
                }
            }
