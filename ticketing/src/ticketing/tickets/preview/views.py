## svg preview
import json
from StringIO import StringIO
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from jsonrpclib import jsonrpc
from pyramid.httpexceptions import HTTPBadRequest

from ticketing.fanstatic import with_bootstrap
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
    return {"organization": context.organization}

#api
"""
raw svg -> normalize svg -> base64 png
"""
@view_defaults(route_name="tickets.preview.api", request_method="POST", renderer="json")
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

