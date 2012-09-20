# coding: utf-8
import logging
logger = logging.getLogger(__file__)

from datetime import datetime
import urllib
import urllib2

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import forget, remember, authenticated_userid
from pyramid.view import view_config
from pyramid.view import view_defaults

from sqlalchemy.orm.exc import NoResultFound

import json

from altaircms.models import DBSession
from altaircms.lib.fanstatic_decorator import with_bootstrap
from altaircms.auth.forms import RoleForm
from .models import Operator, Role, DEFAULT_ROLE, Organization

from . import api
from . import forms
from .api import get_or_404

@view_config(route_name='login', renderer='altaircms:templates/auth/login/login.mako', 
             decorator=with_bootstrap)
@view_config(context='pyramid.httpexceptions.HTTPForbidden', renderer='altaircms:templates/auth/login/login.mako',
             decorator=with_bootstrap)
def login(request):
    logging.info("request user is %s" % request.user)

    if request.user is None:
        message = u"まだログインしていません。ログインしてください。"
    else:
        message = u"このページを閲覧する権限が不足しています。ログアウト後、閲覧権限を持ったログインで再ログインしてください"

    return dict(
        message=message
    )

@view_defaults(route_name="login.self", decorator=with_bootstrap)
class LoginSelfView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(match_param="action=input", renderer="altaircms:templates/auth/login/login.self.mako")
    def input(self):
        form = forms.SelfLoginForm().configure(Organization.query)
        return {"form": form}

    @view_config(match_param="action=login", renderer="altaircms:templates/auth/login/login.self.mako")
    def login(self):
        form = forms.SelfLoginForm(self.request.POST).configure(Organization.query)
        if not form.validate():
            return {"form": form}
        headers = remember(self.request, form.user.user_id)
        url = self.request.route_url('dashboard')
        return HTTPFound(url, headers=headers)


@view_config(route_name='logout')
def logout(request):
    action = api.get_logout_action(request)
    result = action.logout(request)
    return HTTPFound(location=result.return_to, headers=result.headers)


class OAuthLogin(object):
    _urllib2 = urllib2
    def __init__(self, request, **kwargs):
        self.request = request

    @view_config(route_name='oauth_entry')
    def oauth_entry(self):
        oc = api.get_oauth_component(self.request)
        url = oc.create_oauth_entry_url()
        logger.info("*login* oauth entry url: %s" % url)
        return HTTPFound(url)
 
    @view_config(route_name='oauth_callback')
    def oauth_callback(self):
        data = None
        try:
            oc = api.get_oauth_component(self.request)
            code = self.request.GET.get("code")
            grant_type='authorization_code'
            url = oc.create_oauth_token_url(code, grant_type)
            logger.info("*login* access token url: %s" % url)

            data = json.loads(self._urllib2.urlopen(url).read())
            logger.info("*login* access token return: %s" % data)

            api.notify_after_oauth_login(self.request, data)

        except IOError, e:
            logger.exception(e)
            self.request.response.body = str(e)
            return self.request.response

        logger.info("*login* remember user_id = %s" % data["user_id"])
        headers = remember(self.request, data["user_id"])
        url = self.request.route_url('dashboard')
        return HTTPFound(url, headers=headers)


@view_defaults(decorator=with_bootstrap)
class OperatorView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="operator_list", renderer='altaircms:templates/auth/operator/list.mako', permission="operator_read")
    def list(self):
        operators = self.request.allowable(Operator).all()

        return dict(
            operators=operators
        )

    @view_config(route_name="operator", renderer='altaircms:templates/auth/operator/view.mako', permission="operator_read")
    def read(self):
        operator = get_or_404(self.request.allowable(Operator), Operator.id==self.request.matchdict['id'])
        return dict(operator=operator)

    @view_config(route_name="operator", permission="operator_delete",
        request_method="POST", request_param="_method=delete")
    def delete(self):
        operator = get_or_404(self.request.allowable(Operator), Operator.id==self.request.matchdict['id'])
        logged_in_user_id = authenticated_userid(self.request)
        user_id = operator.user_id
        DBSession.delete(operator)

        if user_id == logged_in_user_id:
            return logout(self.request)

        # @TODO 何かしらのフラッシュメッセージ？みたいなのを送り込んで遷移先で表示する
        return HTTPFound(self.request.route_path("operator_list"))




@view_defaults(decorator=with_bootstrap)
class RoleView(object):
    def __init__(self, request):
        self.request = request

    def get_role(self):
        # これはcontextが持つべき
        role_id = self.request.matchdict.get('id')
        try:
            return Role.query.filter_by(id=role_id).one()
        except NoResultFound:
            raise HTTPNotFound

    @view_config(route_name="role_list", request_method="GET", renderer="altaircms:templates/auth/role/list.mako")
    def list(self):
        return dict(
            roles=Role.query.all(),
        )

    @view_config(route_name="role", request_method="GET", renderer="altaircms:templates/auth/role/view.mako")
    def read(self):
        form = RoleForm()
        return dict(
            form=form,
            role=self.get_role(),
        )

    @view_config(route_name="role", request_method="POST", renderer="altaircms:templates/auth/role/view.mako")
    def update(self):
        form = RoleForm(self.request.POST)
        if form.validate():
            role = self.get_role()
            perm = form.data.get('permission')
            role.permissions.append(perm)
            
            return HTTPFound(location=self.request.route_path('role', id=role.id))
        return dict(
            form=form,
            role=self.get_role(),
        )

    @view_config(route_name="role", request_method="POST", request_param="_method=delete")
    def delete(self):
        try:
            role = self.get_role()
            DBSession.delete(role)
        except Exception as e:
            logging.exception(e)
            raise
        return HTTPFound(self.request.route_path("role_list"))

@view_config(route_name="operator_info", renderer='altaircms:templates/auth/operator/info.mako', 
             permission="authenticated", decorator=with_bootstrap)
def operator_info(request):
    operator = request.user
    return {"operator": operator, 
            "organization": operator.organization}


class RolePermissionView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='role_permission', request_method="POST", request_param="_method=delete")
    def delete(self):
        permission = self.request.matchdict.get('id')
        role_id = self.request.matchdict.get('role_id', None)
        role = Role.query.filter_by(id=role_id).one()
        if permission in role.permissions:
            role.permissions.remove(permission)
        
        return HTTPFound(self.request.route_path("role", id=role_id))
