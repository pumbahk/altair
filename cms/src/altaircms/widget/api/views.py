from pyramid.view import view_config
from altaircms.auth.api import get_or_404
from altaircms.page.models import Page
import json

class StructureView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="structure_create", renderer="json", request_method="POST")
    def create(self):
        raise "create must not occur"

    @view_config(route_name="structure_update", renderer="json", request_method="POST")
    def update(self):
        request = self.request
        pk = request.json_body["page"]
        page = get_or_404(request.allowable("Page"), Page.id==pk)
        page.structure = json.dumps(request.json_body["structure"])
        request.context.add(page, flush=True) ## flush?
        return "ok"

    # @view_config(route_name="structure", renderer="json", request_method="DELETE")
    # def delete(self):
    #     print "hor. lay"

    @view_config(route_name="structure_get", renderer="json", request_method="GET")
    def get(self):
        request = self.request
        pk = request.GET["page"]
        page = get_or_404(request.allowable("Page"), Page.id==pk)
        if page.structure:
            return dict(loaded=json.loads(page.structure))
        else:
            return dict(loaded=None)

