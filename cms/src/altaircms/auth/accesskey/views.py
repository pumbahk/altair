# -*- coding:utf-8 -*-

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
import logging
logger = logging.getLogger(__file__)
from altaircms.models import DBSession
from altaircms.viewlib import success_result, failure_result
from altaircms.viewlib import BaseView
from altaircms.viewlib import get_endpoint
from altaircms.viewlib import apikey_required
from altaircms.page.models import Page
from altaircms.event.models import Event
from altaircms.auth.models import PageAccesskey, Organization
from altaircms.auth.api import require_login, get_or_404
from .api import get_page_access_key_control
from .api import get_event_access_key_control
from .api import dict_from_accesskey_string
from altaircms.subscribers import notify_model_create
from .forms import AccessKeyForm

## apiview
@view_config(route_name="external.auth.accesskey.info", renderer="json", 
             custom_predicates=(apikey_required("*dict from accesskey*"), ))
def dict_from_accesskey_view(context, request):
    D = request.params
    organization = get_or_404(Organization.query, Organization.backend_id==D["organization_id"], Organization.auth_source==D["organization_source"])
    return dict_from_accesskey_string(request, D["accesskey"], organization.id)

@view_defaults(route_name="auth.accesskey.pagekey", permission="page_update", 
               custom_predicates=(require_login, )) ##?
class PageAccessKeyView(BaseView):
    @view_config(renderer="json", request_method="POST", match_param="action=delete")
    def delete_accesskey(self):
        page_id = self.request.matchdict["page_id"]
        target_id_list = self.request.params.getall("targets[]")

        page = self.request.allowable(Page).filter_by(id=page_id).first()
        if page is None:
            return failure_result(message="page is not found id = {0}".format(page_id))
        control = get_page_access_key_control(self.request, page)

        targets = control.query_access_key().filter(PageAccesskey.id.in_(target_id_list))
        for t in targets:
            DBSession.delete(t)
        return success_result({"deleted": [t.id for t in targets]})

    @view_config(renderer="json", request_method="POST", match_param="action=create", request_param="operator_id")
    def create_accesskey(self):
        assert unicode(self.request.user.id) == unicode(self.request.POST["operator_id"])

        page_id = self.request.matchdict["page_id"]
        expire = self.request.params.get("expire", None)
                
        page = self.request.allowable(Page).filter_by(id=page_id).first()
        if page is None:
            return failure_result(message="page is not found id = {0}".format(page_id))
        control = get_page_access_key_control(self.request, page)

        key = control.create_access_key(expire=control.expiredate_from_string(expire))
        key.operator_id = self.request.POST["operator_id"]
        DBSession.add(key)
        notify_model_create(self.request, key)
        return success_result({"name": key.name})

@view_defaults(route_name="auth.accesskey.eventkey", permission="event_update", 
               custom_predicates=(require_login, )) ##?
class EventAccessKeyView(BaseView):
    @view_config(renderer="json", request_method="POST", match_param="action=delete")
    def delete_accesskey(self):
        event_id = self.request.matchdict["event_id"]
        target_id_list = self.request.params.getall("targets[]")

        event = self.request.allowable(Event).filter_by(id=event_id).first()
        if event is None:
            return failure_result(message="event is not found id = {0}".format(event_id))
        control = get_event_access_key_control(self.request, event)

        targets = control.query_access_key().filter(PageAccesskey.id.in_(target_id_list))
        for t in targets:
            DBSession.delete(t)
        return success_result({"deleted": [t.id for t in targets]})

    @view_config(renderer="json", request_method="POST", match_param="action=create", request_param="operator_id")
    def create_accesskey(self):
        assert unicode(self.request.user.id) == unicode(self.request.POST["operator_id"])

        event_id = self.request.matchdict["event_id"]
        expire = self.request.params.get("expire", None)
                
        event = self.request.allowable(Event).filter_by(id=event_id).first()
        if event is None:
            return failure_result(message="event is not found id = {0}".format(event_id))
        control = get_event_access_key_control(self.request, event)

        key = control.create_access_key(expire=control.expiredate_from_string(expire))
        key.operator_id = self.request.POST["operator_id"]
        key.scope = "onepage"
        DBSession.add(key)
        notify_model_create(self.request, key)
        return success_result({"name": key.name})

@view_config(route_name="auth.accesskey.detail", permission="authenticated", request_method="GET", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
             renderer="altaircms:templates/auth/accesskey/view.html")
def accesskey_detail(context, request):
    accesskey = get_or_404(request.allowable(PageAccesskey), PageAccesskey.id==request.matchdict["accesskey_id"])
    form = AccessKeyForm(name=accesskey.name, expiredate=accesskey.expiredate, scope=accesskey.scope)
    return {"accesskey": accesskey, "form": form}

@view_config(route_name="auth.accesskey.detail", permission="authenticated", request_method="POST", 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
             renderer="altaircms:templates/auth/accesskey/input.html")
def accesskey_update(context, request):
    accesskey = get_or_404(request.allowable(PageAccesskey), PageAccesskey.id==request.matchdict["accesskey_id"])
    form = AccessKeyForm(request.POST)
    if not form.validate():
        form = AccessKeyForm(name=accesskey.name, expiredate=accesskey.expiredate, scope=accesskey.scope)
        return {"accesskey": accesskey, "form": form}
    else:
        for k in ["scope", "name", "expiredate"]:
            setattr(accesskey, k, getattr(form, k).data)
        accesskey.operator_id = request.user.id
        DBSession.add(accesskey)
        return HTTPFound(request.current_route_path(_query=dict(request.GET)))
