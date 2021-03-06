from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from . import api
from . import forms
from altaircms.page.models import Page    
from altaircms.auth.api import get_or_404
import logging
logger = logging.getLogger(__name__)

@view_defaults(custom_predicates=(require_login,))
class PromotionWidgetView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def _create_or_update(self):
        try:
            data = self.request.json_body["data"].copy()
            data["tag"] = self.context.Tag.query.filter_by(id=data["tag"]).one()
            if data.get("system_tag") and data.get("system_tag") != "__None":
                data["system_tag"] = self.context.Tag.query.filter_by(id=data["system_tag"]).one()
            else:
                data["system_tag"] = None
            use_newstyle = bool(data.get("use_newstyle"))
            if use_newstyle:
                data["use_newstyle"] = 1
            else:
                data.update({"use_newstyle": 0})
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
        except Exception, e:
            logger.exception(str(e))
            return  self.request.json_body.copy()

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

    @view_config(route_name="promotion_widget_dialog", renderer="altaircms.plugins.widget:promotion/dialog.html", request_method="GET")
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

from .api import get_interval_time
from .api import set_interval_time

@view_defaults(renderer="json", route_name="internal.api.promotion.interval")
class PromotionIntervalTimeView(object):
    def _validate(self, request):
        pass

    @view_config(request_method="GET")
    def get(self):
        return {"url": self.request.url, "status": True, "data": get_interval_time()}

    @view_config(request_param="interval_time", request_method="POST")
    def post(self):
        prev = get_interval_time()
        set_interval_time(self.request.POST["interval_time"])
        return {"url": self.request.url, "status": True, "data": get_interval_time(), "prev": prev}

# @view_config(route_name="promotion_slideshow", renderer="altaircms.plugins.widget:promotion/slideshow.html", request_method="GET", 
#              decorator="altaircms.lib.fanstatic_decorator.with_jquery")
# def promotion_slideshow(context, request):
#     pm = api.get_promotion_manager(request)
#     return {"show_image": pm.show_image, "info": pm.promotion_info(request)}
