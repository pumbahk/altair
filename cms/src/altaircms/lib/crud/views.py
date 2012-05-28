from pyramid.httpexceptions import HTTPFound
from altaircms.lib.viewhelpers import FlashMessage
from altaircms.models import DBSession
from altaircms.models import model_from_dict, model_to_dict
import functools
import altaircms.helpers as h
import logging
logger = logging.getLogger(__file__)

from ..flow import api as flow_api

class AfterInput(Exception):
    def __init__(self, form=None, context=None):
        self.form = form
        self.context = context

from altaircms.security import RootFactory
class CRUDResource(RootFactory): ## fixme
    flow_api = flow_api
    def __init__(self, prefix, title, model, form, mapper, endpoint, filter_form, request):
        self.prefix = prefix
        self.title = title
        self.model = model
        self.form = form
        self.mapper = mapper
        self.endpoint = endpoint
        self.filter_form = filter_form
        self.request = request

    def join(self, ac):
        return "%s_%s" % (self.prefix, ac)

    ## search
    def query_form(self, params):
        if self.filter_form:
            return self.filter_form(params)
        else:
            return None

    ## create
    def input_form(self):
        return self.form()

    def confirmed_form(self):
        form = self.form(self.request.POST)
        if form.validate():
            return form
        else:
            ## danger
            self.request.matchdict["action"] = "input"
            raise AfterInput(form=form, context=self)
        
    def create_model_from_form(self, form):
        obj = model_from_dict(self.model, form.data)
        DBSession.add(obj)
        return obj

    def get_model_obj(self, id):
        pks = self.model.__mapper__.primary_key
        assert len(pks) == 1
        
        pk = pks[0].name
        return self.model.query.filter_by(**{pk: id}).one()

    ## listing
    def get_model_query(self):
        return self.model.query

    ## update
    def input_form_from_model(self, obj):
        form = self.form(**model_to_dict(obj))
        return form

    def update_model_from_form(self, id, form):
        obj = self.get_model_obj(id)
        for k, v in form.data.iteritems():
            if v: setattr(obj, k, v)
        DBSession.add(obj)
        return obj

    ## delete
    def delete_model(self, obj):
        DBSession.delete(obj)


class CreateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def _after_input(self): ## context is AfterInput
        form = self.context.form
        return {"master_env": self.context.context,
                "form": form, 
                "display_fields": form.data.keys()}
        
    def input(self):
        form = self.context.input_form()
        raise AfterInput(form=form, context=self.context)

    def confirm(self):
        form = self.context.confirmed_form()
        obj = model_from_dict(self.context.model, form.data)

        ## for don't add to db.
        import transaction
        transaction.abort()

        return {"master_env": self.context,
                "form": form, 
                "obj": obj, 
                "display_fields": form.data.keys()}

    def create_model(self):
        form = self.context.confirmed_form()
        self.context.create_model_from_form(form)
        FlashMessage.success("create", request=self.request)
        return HTTPFound(self.request.route_url(self.context.endpoint), self.request)

class UpdateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _after_input(self):
        form = self.context.form
        return {"master_env": self.context.context,
                "form": form, 
                "display_fields": form.data.keys()}

    def input(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.input_form_from_model(obj)
        raise AfterInput(form=form, context=self.context)

    def confirm(self):
        form = self.context.confirmed_form()
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        for k, v in form.data.iteritems():
            if v: setattr(obj, k, v)

        return {"master_env": self.context,
                "form": form, 
                "obj": obj, 
                "display_fields": form.data.keys()}

    def update_model(self):
        form = self.context.confirmed_form()
        self.context.update_model_from_form(self.request.matchdict["id"], form)
        FlashMessage.success("update", request=self.request)
        return HTTPFound(self.request.route_url(self.context.endpoint), self.request)

class DeleteView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def confirm(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.input_form()
        return {"master_env": self.context,
                "obj": obj, 
                "form": form, 
                "display_fields": form.data.keys()}


    def delete_model(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        self.context.delete_model(obj)
        FlashMessage.success("delete", request=self.request)
        return HTTPFound(self.request.route_url(self.context.endpoint), self.request)

def list_view(context, request):
    qs = context.get_model_query()
    form = context.input_form()

    query_form = context.query_form(request.GET)
    if query_form and "query" in request.GET:
        if query_form:
            qs = query_form.as_filter(qs)

    return {"master_env": context,
            "xs": h.paginate(request, qs, item_count=qs.count()),
            "query_form": query_form, 
            "form": form, 
            "display_fields": form.data.keys()}

## todo: move it
class SimpleCRUDFactory(object):
    Resource = CRUDResource
    def __init__(self, prefix, title, model, form, mapper, filter_form=None):
        self.prefix = prefix
        self.title = title
        self.model = model
        self.form = form
        self.mapper = mapper
        self.filter_form = filter_form

    def _join(self, ac):
        return "%s_%s" % (self.prefix, ac)
        
    def bind(self, config, bind_actions):
        endpoint = self._join("list")
        resource = functools.partial(
            self.Resource, 
            self.prefix, self.title, self.model, self.form, self.mapper, endpoint, self.filter_form)

        if "list" in bind_actions:
            config.add_route(self._join("list"), "/%s" % self.prefix, factory=resource)

            permission = self.prefix+"_read"

            config.add_view(list_view, 
                            permission=permission, 
                            route_name=self._join("list"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/list.mako")

        if "create" in bind_actions:

            config.add_route(self._join("create"), "/%s/create/{action}" % self.prefix, factory=resource)
            config.add_route_flow(self._join("create"), direction_name="crud-create-flow", match_param="action")

            permission = self.prefix + "_create"

            config.add_view(CreateView, match_param="action=input", attr="input", route_name=self._join("create"), 
                           permission=permission
                            )
            config.add_view(CreateView, context=AfterInput, attr="_after_input", route_name=self._join("create"), 
                            decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/create/input.mako")

            config.add_view(CreateView, match_param="action=confirm", attr="confirm",
                            permission=permission, 
                            route_name=self._join("create"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/create/confirm.mako")
            config.add_view(CreateView,
                           permission=permission, 
                            match_param="action=create", attr="create_model", route_name=self._join("create"))

        if "update" in bind_actions:
            config.add_route(self._join("update"), "/%s/update/{id}/{action}" % self.prefix, factory=resource)
            config.add_route_flow(self._join("update"), direction_name="crud-update-flow", match_param="action")

            permission = self.prefix + "_update"

            config.add_view(UpdateView, match_param="action=input", attr="input",
                            permission=permission, 
                            route_name=self._join("update"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/update/input.mako")
            config.add_view(UpdateView, context=AfterInput, attr="_after_input", route_name=self._join("update"), 
                            decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/update/input.mako")
            config.add_view(UpdateView, match_param="action=confirm", attr="confirm",
                            permission=permission, 
                            route_name=self._join("update"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/update/confirm.mako")
            config.add_view(UpdateView, 
                            permission=permission, 
                            match_param="action=update", attr="update_model", route_name=self._join("update"), )

        if "delete" in bind_actions:
            config.add_route(self._join("delete"), "/%s/delete/{id}/{action}" % self.prefix, factory=resource)
            config.add_route_flow(self._join("delete"), direction_name="crud-delete-flow", match_param="action")

            permission = self.prefix + "_delete"

            config.add_view(DeleteView, match_param="action=confirm", attr="confirm",
                            permission=permission, 
                            route_name=self._join("delete"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/delete/confirm.mako")
            config.add_view(DeleteView, 
                            permission=permission, 
                            match_param="action=delete", attr="delete_model", route_name=self._join("delete"))
