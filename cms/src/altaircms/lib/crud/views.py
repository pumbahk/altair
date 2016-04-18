# -*- encoding:utf-8 -*-
import transaction
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from altaircms.helpers.viewhelpers import FlashMessage
from altaircms.models import DBSession
from altaircms.models import model_from_dict, model_to_dict
import functools
import altaircms.helpers as h
import logging
logger = logging.getLogger(__file__)
from altaircms.security import RootFactory
from altaircms.helpers.viewhelpers import get_endpoint
from altaircms.subscribers import notify_model_create ## too-bad

from sqlalchemy.sql.operators import ColumnOperators
logger = logging.getLogger(__file__)

"""
todo: resourceを登録する形式に変更
"""
class AfterInput(Exception):
    def __init__(self, form=None, context=None):
        self.form = form
        self.context = context
        self.circle_type = context.circle_type

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
    def __init__(self, prefix, title, model, form, mapper, endpoint, filter_form,
                 request,
                 after_input_context=None, 
                 override_templates=None, 
                 create_event=None, update_event=None, delete_event=None, 
                 circle_type="circle-master"):
        RootFactory.__init__(self, request)
        self.override_templates = override_templates or {}
        self.prefix = prefix
        self.title = title
        self.model = model
        self.form = form
        self.mapper = mapper
        self.endpoint = endpoint
        self.filter_form = filter_form

        self.create_event = create_event
        self.update_event = update_event
        self.delete_event = delete_event
        self.AfterInput = after_input_context
        self.circle_type = circle_type

    def join(self, ac):
        return "%s_%s" % (self.prefix, ac)

    ## endpoint
    def get_endpoint(self):
        endpoint = get_endpoint(self.request)
        return endpoint or self.request.route_url(self.endpoint or "dashboard")

    ## search
    def query_form(self, params):
        if self.filter_form:
            form = self.filter_form(params)
            if hasattr(form, "configure"):
                form.configure(self.request)
        else:
            return None

    ## create
    def input_form(self, *args, **kwargs):
        form = self.form(*args, **kwargs)
        if hasattr(form, "configure"):
            form.configure(self.request)
        return form

    def confirmed_form(self, obj=None):
        form = self.form(self.request.POST)
        if hasattr(form, "configure"):
            form.configure(self.request)
        if form.validate():
            if not hasattr(form, "object_validate") or form.object_validate(obj):
                return form
            ## danger
        self.request.matchdict["action"] = "input"
        raise self.AfterInput(form=form, context=self)

    def create_model_from_form(self, form):
        from altaircms.auth.helpers import get_authenticated_organization
        _ = get_authenticated_organization(self.request)
        obj = model_from_dict(self.model, form.data)
        DBSession.add(obj)

        ## todo: 疎
        notify_model_create(self.request, obj, form.data)
        DBSession.flush()
        if self.create_event:
            ## IModelEvent
            self.request.registry.notify(self.create_event(self.request, obj, form.data))

        return obj

    def get_model_obj(self, id):
        if hasattr(self, "obj") and self.obj.id == id:
            return self.obj
        pks = self.model.__mapper__.primary_key
        assert len(pks) == 1
        
        pk = pks[0].name
        self.obj = self.model.query.filter_by(**{pk: id}).first()
        if self.obj is None:
            logger.warn("data is not found model={model}, id={id}".format(model=self.model.__name__, id=id))
            raise HTTPNotFound("data is not found")
        return self.obj

    ## listing
    def get_model_query(self):
        ## todo 疎結合
        if hasattr(self.request, "organization"):
            return self.request.allowable(self.model)
        else:
            return self.model.query

    ## update
    def input_form_from_model(self, obj, **kwargs):
        if hasattr(obj, "to_dict"):
            params = obj.to_dict()
        else:
            params = model_to_dict(obj)
        params.update(kwargs)
        form = self.form(**params)
        if hasattr(form, "configure"):
            form.configure(self.request)
        return form

    def update_model_from_form(self, obj, form):
        # Put trackingcode together
        trackingcode_parts, trackingcode_genre, trackingcode_eventcode, trackingcode_date = None, None, None, None
        for k, v in form.data.iteritems():
            if k == "trackingcode_parts":
                trackingcode_parts = v
            elif k == "trackingcode_genre":
                trackingcode_genre = v
            elif k == "trackingcode_eventcode":
                trackingcode_eventcode = v
            elif k == "trackingcode_date":
                trackingcode_date = v
            else:
                setattr(obj, k, v)
        if None not in [trackingcode_parts, trackingcode_genre, trackingcode_eventcode, trackingcode_date]:
            obj.trackingcode = "_".join([trackingcode_parts, trackingcode_genre, trackingcode_eventcode, trackingcode_date.strftime("%Y%m%d")])

        DBSession.add(obj)

        if self.update_event:
            self.request.registry.notify(self.update_event(self.request, obj, form.data))
        return obj

    ## delete
    def delete_model(self, obj):
        if self.delete_event:
            self.request.registry.notify(self.delete_event(self.request, obj, {}))
        if hasattr(obj, "delete"):
            obj.delete(session=DBSession)
        DBSession.delete(obj)

class CreateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def _after_input(self): ## context is AfterInput
        form = self.context.form
        master_env = self.context.context
        if "create" in getattr(master_env, "override_templates", None):
            self.request.override_renderer = master_env.override_templates["create"]
        return {"master_env": master_env,
                "form": form, 
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}

    def copied_input(self):
        obj = self.context.get_model_obj(self.request.params["id"])
        form = self.context.input_form_from_model(obj)
        raise self.context.AfterInput(form=form, context=self.context)
        
    def input(self):
        form = self.context.input_form(**self.request.GET)
        raise self.context.AfterInput(form=form, context=self.context)

    def confirm(self):
        form = self.context.confirmed_form()
        obj = ModelFaker(model_from_dict(self.context.model, form.data))
        transaction.abort() ## for
        return {"master_env": self.context,
                "form": form, 
                "obj": obj, 
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}

    def create_model(self):
        form = self.context.confirmed_form()
        obj = self.context.create_model_from_form(form)
        url = self.request.route_path(self.context.join("update"), id=obj.id, action="input")
        mes = u'%sを作成しました <a href="%s">新しく作成されたデータを編集</a>' % (self.context.title, url)
        FlashMessage.success(mes, request=self.request)
        return HTTPFound(self.context.get_endpoint())

class UpdateView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _after_input(self):
        form = self.context.form
        master_env = self.context.context
        if "update" in getattr(master_env, "override_templates", None):
            self.request.override_renderer = master_env.override_templates["update"]
        return {"master_env": master_env,
                "form": form, 
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}

    def input(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.input_form_from_model(obj, **self.request.GET)
        raise self.context.AfterInput(form=form, context=self.context)

    def confirm(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.confirmed_form(obj=obj)
        obj = ModelFaker(obj)
        trackingcode_parts, trackingcode_genre, trackingcode_eventcode, trackingcode_date = None, None, None, None
        for k, v in form.data.iteritems():
            if k == "trackingcode_parts":
                trackingcode_parts = v
            elif k == "trackingcode_genre":
                trackingcode_genre = v
            elif k == "trackingcode_eventcode":
                trackingcode_eventcode = v
            elif k == "trackingcode_date":
                trackingcode_date = v
            else:
                setattr(obj, k, v)
        if None not in [trackingcode_parts, trackingcode_genre, trackingcode_eventcode, trackingcode_date]:
            obj.trackingcode = "_".join([trackingcode_parts, trackingcode_genre, trackingcode_eventcode, trackingcode_date.strftime("%Y%m%d")])

        return {"master_env": self.context,
                "obj": obj, 
                "form": form, 
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}

    def update_model(self):
        before_obj = self.context.get_model_obj(self.request.matchdict["id"])
        form = self.context.confirmed_form(obj=before_obj)
        obj = self.context.update_model_from_form(before_obj, form)
        url = self.request.route_path(self.context.join("update"), id=obj.id, action="input")
        mes = u'%sを編集しました <a href="%s">変更されたデータを編集</a>' % (self.context.title, url)
        FlashMessage.success(mes, request=self.request)
        return HTTPFound(self.context.get_endpoint())

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
                "display_fields": getattr(form,"__display_fields__", None) or form.data.keys()}


    def delete_model(self):
        obj = self.context.get_model_obj(self.request.matchdict["id"])
        self.context.delete_model(obj)
        FlashMessage.success(u"%sを削除しました" % self.context.title, request=self.request)
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
    def __init__(self, prefix, title, model, form, mapper, 
                 filter_form=None):
        self.prefix = prefix
        self.title = title
        self.model = model
        self.form = form
        self.mapper = mapper
        self.filter_form = filter_form

    def _join(self, ac):
        return "%s_%s" % (self.prefix, ac)

    def bind(self, config, bind_actions, events=None,
             has_auto_generated_permission=True, 
             after_input_context=AfterInput, 
             endpoint=None, 
             circle_type="circle-master", 
             override_templates=None, 
             **default_kwargs):

        after_input_context = config.maybe_dotted(after_input_context)
        self.endpoint = endpoint or self._join("list")
        self.resource = resource = functools.partial(
            self.Resource, 
            self.prefix, self.title, self.model, self.form, self.mapper, endpoint, self.filter_form, 
            after_input_context=after_input_context, circle_type=circle_type, override_templates=override_templates, 
            **(events or {})) #events. e.g create_event, update_event, delete_event

        ## individual add view function.
        def _add_view(view_fn, **kwargs):
            for k, v in default_kwargs.iteritems():
                if not k in kwargs:
                    kwargs[k] = v
            if has_auto_generated_permission:
                permission = self.prefix+"_read"
                kwargs["permission"] = permission
            else:
                kwargs["permission"] = "authenticated"
            config.add_view(view_fn, **kwargs)


        if "list" in bind_actions:
            config.add_route(self._join("list"), "/%s" % self.prefix, factory=resource)

            _add_view(list_view, 
                     route_name=self._join("list"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/list.html")

        if "create" in bind_actions:

            config.add_route(self._join("create"), "/%s/create/{action}" % self.prefix, factory=resource)
            _add_view(CreateView, match_param="action=copied_input", attr="copied_input", route_name=self._join("create"))
            _add_view(CreateView, match_param="action=input", attr="input", route_name=self._join("create"))
            config.add_view(CreateView, context=AfterInput, attr="_after_input", route_name=self._join("create"), 
                            decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/create/input.html")
            _add_view(CreateView, match_param="action=confirm", attr="confirm",
                      route_name=self._join("create"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/create/confirm.html")
            _add_view(CreateView, match_param="action=create", attr="create_model", route_name=self._join("create"))

        if "update" in bind_actions:
            config.add_route(self._join("update"), "/%s/update/{id}/{action}" % self.prefix, factory=resource)

            _add_view(UpdateView, match_param="action=input", attr="input",
                      route_name=self._join("update"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap",
                      renderer="altaircms:lib/crud/update/input.html")
            config.add_view(UpdateView, context=AfterInput, attr="_after_input", route_name=self._join("update"), 
                            decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/update/input.html")
            _add_view(UpdateView, match_param="action=confirm", attr="confirm",
                      route_name=self._join("update"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/update/confirm.html")
            _add_view(UpdateView, 
                      match_param="action=update", attr="update_model", route_name=self._join("update"), )

        if "delete" in bind_actions:
            config.add_route(self._join("delete"), "/%s/delete/{id}/{action}" % self.prefix, factory=resource)

            _add_view(DeleteView, match_param="action=confirm", attr="confirm",
                            route_name=self._join("delete"), decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", renderer="altaircms:lib/crud/delete/confirm.html")
            _add_view(DeleteView, 
                            match_param="action=delete", attr="delete_model", route_name=self._join("delete"))
