# -*- encoding:utf-8 -*-

from pyramid.httpexceptions import HTTPFound
from altaircms.lib.viewhelpers import FlashMessage
from altaircms.models import DBSession
from altaircms.models import model_from_dict, model_to_dict
import functools
import altaircms.helpers as h
import logging
logger = logging.getLogger(__file__)
from altaircms.security import RootFactory
from ..flow import api as flow_api


from sqlalchemy.sql.operators import ColumnOperators

class AfterInput(Exception):
    def __init__(self, form=None, context=None):
        self.form = form
        self.context = context

class ModelFaker(object):
    def __init__(self, obj):
        self.__dict__["obj"] = obj

    def __getattr__(self, k, v=None):
        return getattr(self.__dict__["obj"], k, v)

    def to_dict(self):
        container = self
        obj = self.__dict__["obj"]
        return {k: getattr(container, k) for k, v in obj.__class__.__dict__.iteritems() \
                if isinstance(v, ColumnOperators)}

class CRUDResource(RootFactory): ## fixme
    flow_api = flow_api
    def __init__(self, prefix, title, model, form, mapper, endpoint, filter_form,
                 request,
                 create_event=None, update_event=None, delete_event=None):
        self.prefix = prefix
        self.title = title
        self.model = model
        self.form = form
        self.mapper = mapper
        self.endpoint = endpoint
        self.filter_form = filter_form
        self.request = request

        self.create_event = create_event
        self.update_event = update_event
        self.delete_event = delete_event

    def join(self, ac):
        return "%s_%s" % (self.prefix, ac)

    ## endpoint
    CMS_ENDPOINT = "cms:endpoint"
    def set_endpoint(self):
        session = self.request.session
        session[self.CMS_ENDPOINT] = self.request.referrer

    def get_endpoint(self):
        session = self.request.session
        endpoint = session.get(self.CMS_ENDPOINT)
        if endpoint:
            return endpoint
        return self.request.route_url(self.endpoint)

    ## search
    def query_form(self, params):
        if self.filter_form:
            return self.filter_form(params)
        else:
            return None

    ## create
    def input_form(self, *args, **kwargs):
        return self.form(*args, **kwargs)

    def confirmed_form(self, obj=None):
        form = self.form(self.request.POST)
        if form.validate():
            if not hasattr(form, "object_validate") or form.object_validate(obj):
                return form
            ## danger
        self.request.matchdict["action"] = "input"
        raise AfterInput(form=form, context=self)

    def create_model_from_form(self, form):
        obj = model_from_dict(self.model, form.data)
        DBSession.add(obj)

        if self.create_event:
            ## IModelEvent
            self.request.registry.notify(self.create_event(self.request, obj, form.data))
        DBSession.flush()
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

    def update_model_from_form(self, obj, form):
        for k, v in form.data.iteritems():
            if v: setattr(obj, k, v)
        DBSession.add(obj)

        if self.update_event:
            self.request.registry.notify(self.update_event(self.request, obj, form.data))
        return obj

    ## delete
    def delete_model(self, obj):
        if self.delete_event:
            self.request.registry.notify(self.delete_event(self.request, obj, {}))
        DBSession.delete(obj)

class CreateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def _after_input(self): ## context is AfterInput
        form = self.context.form
        return {"master_env": self.context.context,
                "form": form, 
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}
        
    def input(self):
        self.context.set_endpoint()
        form = self.context.input_form(self.request.GET)
        raise AfterInput(form=form, context=self.context)

    def confirm(self):
        form = self.context.confirmed_form()
        obj = ModelFaker(model_from_dict(self.context.model, form.data))

        return {"master_env": self.context,
                "form": form, 
                "obj": obj, 
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}

    def create_model(self):
        form = self.context.confirmed_form()
        obj = self.context.create_model_from_form(form)
        mes = u'create <a href="%s">新しく作成されたデータを編集</a>' % self.request.route_path(self.context.join("update"), id=obj.id, action="input")
        FlashMessage.success(mes, request=self.request)
        return HTTPFound(self.context.get_endpoint())

class UpdateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _after_input(self):
        form = self.context.form
        return {"master_env": self.context.context,
                "form": form, 
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}

    def input(self):
        self.context.set_endpoint()

        obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.input_form_from_model(obj)
        raise AfterInput(form=form, context=self.context)

    def confirm(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.confirmed_form(obj=obj)
        obj = ModelFaker(obj)

        for k, v in form.data.iteritems():
            setattr(obj, k, v)

        return {"master_env": self.context,
                "obj": obj, 
                "form": form, 
                "obj": obj, 
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}

    def update_model(self):
        before_obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.confirmed_form(obj=before_obj)

        obj = self.context.update_model_from_form(before_obj, form)
        mes = u'update <a href="%s">変更されたデータを編集</a>' % self.request.route_path(self.context.join("update"), id=obj.id, action="input")
        FlashMessage.success(mes, request=self.request)
        return HTTPFound(self.context.get_endpoint())

class DeleteView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def confirm(self):
        self.context.set_endpoint()

        obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.input_form()
        return {"master_env": self.context,
                "obj": obj, 
                "form": form, 
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}


    def delete_model(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        self.context.delete_model(obj)
        FlashMessage.success("delete", request=self.request)
        return HTTPFound(self.context.get_endpoint())

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
            "display_fields": getattr(form, "__display_fields__", None) or form.data.keys()}

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

    def bind(self, config, bind_actions, events=None):
        endpoint = self._join("list")
        resource = functools.partial(
            self.Resource, 
            self.prefix, self.title, self.model, self.form, self.mapper, endpoint, self.filter_form, 
            **(events or {})) #events. e.g create_event, update_event, delete_event

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
