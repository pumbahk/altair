from pyramid.httpexceptions import HTTPFound
from altaircms.lib.viewhelpers import FlashMessage
from altaircms.models import DBSession
from altaircms.models import model_from_dict, model_to_dict
import functools
import altaircms.helpers as h

class AfterInput(Exception):
    pass

class CRUDResourceFactory(object):
    def __init__(self, title, model, form, mapper, endpoint):
        self.title = title
        self.model = model
        self.form = form
        self.mapper = mapper
        self.endpoint = endpoint
        
    def create(self, name, base=None):
        base = base or CRUDResource
        def __init__(self, request):
            self.request = request

        attrs = {"title": self.title, 
                 "model": self.model, 
                 "form": self.form, 
                 "mapper": self.mapper, 
                 "endpoint": self.endpoint, 
                 "__init__": __init__}
        return type(name, (base, ), attrs) ## too-bad
    
class CRUDResource(object):
    title, model, form, mapper, endpoint = None, None, None, None, None
    ## create
    def input_form(self):
        return self.form()

    def confirmed_form(self):
        form = self.form(self.request.POST)
        if form.validate():
            return form
        else:
            raise AfterInput(form=form)
        
    def create_model_from_form(self, form):
        obj = model_from_dict(self.model, form.data)
        DBSession.add(obj)
        return obj

    def get_model_obj(self, id):
        self.model.query.filter_by(id=id).one()

    ## listing
    def get_model_query(self):
        return self.model.query

    ## update
    def input_form_from_model(self, id):
        obj = self.get_model_obj()
        form = self.form(model_to_dict(obj))
        return form

    update_model_from_form = create_model_from_form

    ## delete
    def delete_model(self, obj):
        DBSession.delete(obj)


class CreateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def _after_input(self):
        form = self.request._form
        return {"context": self.context,
                "title": self.context.title, 
                "form": form, 
                "display_fields": form.data.keys()}
        
    def input(self):
        form = self.context.input_form()
        self.request._form = form
        raise AfterInput

    def confirm(self):
        form = self.context.confirmed_form()
        self.request._form = form
        raise AfterInput

    def create_model(self):
        form = self.context.confirmed_form()
        self.context.create_model_from_form(form)
        FlashMessage.success("create", request=self.request)
        return HTTPFound(self.context.endpoint, self.request)

class UpdateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _after_input(self):
        form = self.request._form
        return {"context": self.context,
                "title": self.context.title, 
                "form": form, 
                "display_fields": form.data.keys()}

    def input(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.input_form_from_model(obj)
        self.request._form = form
        raise AfterInput

    def confirm(self):
        form = self.context.confirmed_form()
        self.request._form = form
        raise AfterInput

    def update_model(self):
        form = self.context.confirmed_form()
        self.context.update_model_from_form(form)
        FlashMessage.success("update", request=self.request)
        return HTTPFound(self.context.endpoint, self.request)

class DeleteView(object):
    endpoint = None
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def confirm(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.input_form()
        return {"context": self.context,
                "x": obj, 
                "title": self.context.title, 
                "form": form, 
                "display_fields": form.data.keys()}


    def delete_model(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        self.context.delete_model(obj)
        FlashMessage.success("delete", request=self.request)
        return HTTPFound(self.context.endpoint, self.request)

def list_view(context, request):
    xs = context.get_model_query()
    form = context.input_form()
    return {"context": context,
            "xs": h.paginate(request, xs),
            "title": context.title, 
            "form": form, 
            "display_fields": form.data.keys()}

## todo: move it
class SimpleCRUDFactory(object):
    Resource = CRUDResource
    def __init__(self, prefix, title, model, form, mapper):
        self.prefix = prefix
        self.title = title
        self.model = model
        self.form = form
        self.mapper = mapper

    def _join(self, ac):
        return "%s_%s" % (self.prefix, ac)

    def bind(self, config):
        endpoint = self._join("list")
        resource_factory = CRUDResourceFactory(self.title, self.model, self.form, self.mapper, endpoint)
        resource = resource_factory.create("crud"+self.prefix+"Resource", self.Resource)
        resource.join = self._join

        ## list
        config.add_route(self._join("list"), "/%s", factory=resource)
        config.add_view(list_view, 
                        decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/list.mako")

        ## create
        config.add_route(self._join("create"), "/%s/create/{action}", factory=resource)
        config.add_route_flow(self._join("create"), direction_name="crud-create-flow", match_param="action")

        config.add_view(CreateView, match_param="action=input", attr="input",
                        decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/create/input.mako")
        config.add_view(CreateView, match_param="action=confirm", attr="confirm",
                        decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/create/confirm.mako")
        config.add_view(CreateView, match_param="action=create", attr="create_model")

        ## update
        config.add_route(self._join("update"), "/%s/update/{id}/{action}", factory=resource)
        config.add_route_flow(self._join("update"), direction_name="crud-update-flow", match_param="action")
        config.add_view(UpdateView, match_param="action=input", attr="input",
                        decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/update/input.mako")
        config.add_view(UpdateView, match_param="action=confirm", attr="confirm",
                        decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/update/confirm.mako")
        config.add_view(UpdateView, match_param="action=update", attr="update_model")

        ## delete
        config.add_route(self._join("delete"), "/%s/delete/{id}/{action}", factory=resource)
        config.add_route_flow(self._join("delete"), direction_name="crud-delete-flow", match_param="action")
        config.add_view(DeleteView, match_param="action=confirm", attr="confirm",
                        decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/delete/confirm.mako")
        config.add_view(DeleteView, match_param="action=delete", attr="delete_model")
