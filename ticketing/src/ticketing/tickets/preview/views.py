## svg preview
import json
from StringIO import StringIO
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from jsonrpclib import jsonrpc
from pyramid.httpexceptions import HTTPBadRequest

from ticketing.fanstatic import with_bootstrap
from ticketing.core import models as c_models
from .api import SVGPreviewCommunication
from ..cleaner.api import get_validated_svg_cleaner, skip_needless_part
from .fillvalues import template_collect_vars
from .fillvalues import template_fillvalues

@view_config(route_name="tickets.preview", request_method="GET", renderer="ticketing:templates/tickets/preview.html", 
             decorator=with_bootstrap)
def preview_ticket(context, request):
    apis = {
        "normalize": request.route_path("tickets.preview.api", action="normalize"), 
        "previewbase64": request.route_path("tickets.preview.api", action="preview.base64"), 
        "collectvars": request.route_path("tickets.preview.api", action="collectvars"), 
        "fillvalues": request.route_path("tickets.preview.api", action="fillvalues")
        }
    return {"apis": json.dumps(apis)}

@view_config(route_name="tickets.preview", request_method="POST", 
             request_param="svgfile")
def preview_ticket_post(context, request):
    preview = SVGPreviewCommunication.get_instance(request)

    svgio = request.POST["svgfile"].file 
    cleaner = get_validated_svg_cleaner(svgio, exc_class=HTTPBadRequest)
    svgio = cleaner.get_cleaned_svgio()
    try:
        imgdata_base64 = preview.communicate(request, svgio.getvalue())
        return preview.as_filelike_response(request, imgdata_base64)
    except jsonrpc.ProtocolError, e:
        raise HTTPBadRequest(str(e))

@view_config(route_name="tickets.preview.combobox", request_method="GET", renderer="ticketing:templates/tickets/combobox.html", 
             decorator=with_bootstrap, permission="event_editor")
def combbox_for_preview(context, request):
    apis = {
        "organization_list": request.route_path("tickets.preview.combobox.api", model="organization"), 
        "event_list": request.route_path("tickets.preview.combobox.api", model="event"), 
        "performance_list": request.route_path("tickets.preview.combobox.api", model="performance"), 
        "product_list": request.route_path("tickets.preview.combobox.api", model="product"), 
        }
    return {"organization": context.organization, "apis": json.dumps(apis)}

#api
"""
raw svg -> normalize svg -> base64 png
"""
@view_defaults(route_name="tickets.preview.combobox.api", request_method="POST", renderer="json")
class PreviewApiView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(match_param="action=normalize", request_param="svg")
    def preview_api_normalize(self):
        try:
            svgio = StringIO(unicode(self.request.POST["svg"]).encode("utf-8")) #unicode only
            cleaner = get_validated_svg_cleaner(svgio, exc_class=Exception)
            svgio = cleaner.get_cleaned_svgio()
            return {"status": True, "data": svgio.getvalue()}
        except Exception, e:
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}

    @view_config(match_param="action=collectvars", request_param="svg")
    def preview_collectvars(self):
        svg = self.request.POST["svg"]
        try:
            return {"status": True, "data": list(sorted(template_collect_vars(svg)))}
        except Exception, e:
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}

    @view_config(match_param="action=fillvalues", request_param="svg")
    def preview_fillvalus(self):
        svg = self.request.POST["svg"]
        try:
            params = json.loads(self.request.POST["params"])
            dels = []
            for k in params:
                if not params[k]:
                    dels.append(k)
            for k in dels:
                del params[k]
            return {"status": True, "data": template_fillvalues(svg, params)}
        except Exception, e:
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}

    @view_config(match_param="action=preview.base64", request_param="svg")
    def preview_ticket_post64(self):
        preview = SVGPreviewCommunication.get_instance(self.request)
        # svg = skip_needless_part(self.request.POST["svg"])
        svg = self.request.POST["svg"]
        try:
            imgdata_base64 = preview.communicate(self.request, svg)
            return {"status": True, "data":imgdata_base64}
        except jsonrpc.ProtocolError, e:
            return {"status": False, "message": "%s: %s" % (e.__class__.__name__, str(e))}


@view_defaults(route_name="tickets.preview.combobox.api", request_method="GET", renderer="json")
class PreviewApiView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    result = [{"name": "foo", "pk": 1},{"name": "fooo", "pk": 2},{"name": "foooo", "pk": 3},{"name": "fooooo", "pk": 4},{"name": "foooooooo", "pk": 5}, ]

    @view_config(match_param="model=organization")
    def organization(self):
        o = self.context.organization
        return {"status": True, "data": [{"name": o.name, "pk": o.id}]}

    @view_config(match_param="model=event", request_param="organization")
    def event(self):
        qs = c_models.Event.query.filter(c_models.Organization.id==self.request.GET["organization"]) #filter?
        seq = [{"pk": q.id, "name": q.title} for q in qs]
        return {"status": True, "data": seq}

    @view_config(match_param="model=performance", request_param="event")
    def performance(self):
        qs = c_models.Performance.query.filter(c_models.Performance.event_id==self.request.GET["event"], 
                                              c_models.Event.organization_id==self.request.GET["organization"]) #filter?
        seq = [{"pk": q.id, "name": q.name} for q in qs]
        return {"status": True, "data": seq}

    @view_config(match_param="model=product", request_param="performance")
    def product(self):
        qs = c_models.Product.query.filter(c_models.Product.event_id==self.request.GET["event"],
                                           c_models.Product.id==c_models.ProductItem.product_id, 
                                           c_models.ProductItem.performance_id==self.request.GET["performance"])
        seq = [{"pk": q.id, "name": "%s(%se)" % (q.name, q.price)} for q in qs]
        return {"status": True, "data": seq}

