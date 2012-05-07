from pyramid.httpexceptions import HTTPFound
from altaircms.lib.viewhelpers import FlashMessage
from altaircms.lib.fanstatic_decorator import with_bootstrap
from altaircms.models import DBSession
from altaircms.models import model_from_dict

class AfterInput(Exception):
    pass

class SimpleCRUDViewFactory(object):
    def __init__(self, prefix, title, model, form):
        self.prefix = prefix
        self.title = title
        self.model = model
        self.form = form

    def _join(self, ac):
        return "%s_%s" % (self.prefix, ac)

    def generate(self, config):

        def list(request):
            xs = self.model.query
            form = self.form()
            return {"xs": xs, 
                    "master_env": self, 
                    "title":self.title, 
                    "form":form, 
                    "display_fields": form.data.keys()}

        def reinput_list(request):
            xs = self.model.query
            form = request._form
            return {"xs": xs, 
                    "master_env": self, 
                    "title":self.title, 
                    "form":form, 
                    "display_fields": form.data.keys()}
        
        def create(request):
            form = self.form(request.POST)
            if form.validate():
                obj = model_from_dict(self.model, form.data)
                DBSession.add(obj)
                FlashMessage.success("create", request=request)
            else:
                # FlashMessage.error(form.errors, request=request)
                request._form = form
                raise AfterInput
            return HTTPFound(request.route_path(self._join("list")), request)

        def delete(request):
            obj = self.model.query.filter_by(id=request.matchdict["id"]).one()
            DBSession.delete(obj)
            FlashMessage.success("delete", request=request)
            return HTTPFound(request.route_path(self._join("list")), request)

        config.add_view(route_name=self._join("list"), decorator=with_bootstrap,
                        request_method="GET", renderer="altaircms:lib/crud/list.mako", view=list)
        config.add_route(self._join("list"), "/%s/" % self.prefix)
        config.add_view(route_name=self._join("create"), request_method="POST", view=create)
        config.add_route(self._join("create"), "/%s/create" % self.prefix)
        config.add_view(route_name=self._join("create"), decorator=with_bootstrap,
                        context=AfterInput, renderer="altaircms:lib/crud/list.mako", view=reinput_list)
        config.add_view(route_name=self._join("delete"), request_method="POST", view=delete)
        config.add_route(self._join("delete"), "/%s/{id}/delete" % self.prefix)

