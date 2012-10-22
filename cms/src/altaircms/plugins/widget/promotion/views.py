from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from . import api
from . import forms
from altaircms.page.models import Page    
from altaircms.auth.api import get_or_404

@view_defaults(custom_predicates=(require_login,))
class PromotionWidgetView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    def _create_or_update(self):
        data = self.request.json_body["data"]
        data["kind"] = self.context.Kind.query.filter_by(id=data["kind"]).one()
        page_id = self.request.json_body["page_id"]
        context = self.request.context
        widget = context.get_widget(self.request.json_body.get("pk"))
        widget = context.update_data(widget,
                                     page_id=page_id, 
                                     **data)
        context.add(widget, flush=True)
        r = self.request.json_body.copy()
        r.update(pk=widget.id)
        return r

    @view_config(route_name="promotion_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="promotion_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="promotion_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="promotion_widget_dialog", renderer="altaircms.plugins.widget:promotion/dialog.mako", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.GET["page"])
        form = forms.PromotionWidgetForm(**widget.to_dict()).configure(self.request, page)
        return {"widget": widget, "form": form}

@view_config(route_name="api_promotion_main_image", request_method="GET", request_param="promotion_unit_id", renderer="json")
def promotion_main_image(context, request):
    pm = api.get_promotion_manager(request)
    return pm.main_image_info(request)

# @view_config(route_name="promotion_slideshow", renderer="altaircms.plugins.widget:promotion/slideshow.mako", request_method="GET", 
#              decorator="altaircms.lib.fanstatic_decorator.with_jquery")
# def promotion_slideshow(context, request):
#     pm = api.get_promotion_manager(request)
#     return {"show_image": pm.show_image, "info": pm.promotion_info(request)}
