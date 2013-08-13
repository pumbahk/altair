from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from altaircms.lib.itertools import group_by_n
from . import forms
from altaircms.formhelpers import AlignChoiceField
from webob.multidict import MultiDict
import logging
import json
logger = logging.getLogger(__name__)

@view_defaults(custom_predicates=(require_login,))
class ImageWidgetView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _create_or_update(self):
        try:
            form = forms.ImageInfoForm(MultiDict(self.request.json_body["data"], page_id=self.request.json_body["page_id"]))
            if not form.validate():
                logger.warn(str(form.errors))
                r = self.request.json_body.copy()
                r.update(pk=None, asset_id=None)
                return r
            params = form.data
            widget = self.context.get_widget(self.request.json_body.get("pk"))
            params["asset_id"] = form.data.get("asset_id")
            if widget and params.get("asset_id") is None:
                params["asset_id"] = widget.asset_id
            widget = self.context.update_data(widget, **params)
            self.context.add(widget, flush=True)

            r = self.request.json_body.copy()
            r.update(pk=widget.id, asset_id=widget.asset_id)
            return r
        except Exception, e:
            logger.exception(str(e))
            r = self.request.json_body.copy()
            r.update(pk=None, asset_id=None)
            return r

    @view_config(route_name="image_widget_create", renderer="json", request_method="POST")        
    def create(self):
        return self._create_or_update()

    @view_config(route_name="image_widget_update", renderer="json", request_method="POST")        
    def update(self):
        return self._create_or_update()

    @view_config(route_name="image_widget_delete", renderer="json", request_method="POST")        
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="image_widget_dialog", renderer="altaircms.plugins.widget:image/dialog.html", request_method="GET")
    def dialog(self):
        N = 4
        assets = group_by_n(self.request.context.get_asset_query(), N)
        widget = self.request.context.get_widget(self.request.GET.get("pk"))

        if widget.width == 0:
            widget.width = ""
        if widget.height == 0:
            widget.height = ""
        params = widget.to_dict()
        params.update(widget.attributes or {})      
        form = forms.ImageInfoForm(**AlignChoiceField.normalize_params(params))
        return {"assets": assets, "form": form, "widget": widget}


    @view_config(route_name="image_widget_search", renderer="json", request_method="POST")
    def updates_view(self):
        search_word = self.request.POST['search_word']

        N = 4
        assets = None
        if search_word:
            assets = group_by_n(self.request.context.search_asset(search_word), N)
        else:
            assets = group_by_n(self.request.context.get_asset_query(), N)

        import logging
        logger = logging.getLogger(__file__)
        logger.error("JJJJJSOSSOSOSOSOS")


        for groupNo, group in enumerate(assets):
            logger.error("groupNo =" + str(groupNo))
            for img in group:
                logger.error("imgID =" + str(img.id))

        return [
            100,
            200,
        ]