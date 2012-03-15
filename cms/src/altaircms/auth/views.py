# coding: utf-8
from datetime import datetime
import urlparse

from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPUnauthorized, HTTPNotFound
from pyramid.security import forget, remember, authenticated_userid
from pyramid.view import view_config
from pyramid.url import route_url

from sqlalchemy.orm.exc import NoResultFound

import oauth2
import transaction
import json

from altaircms.views import BaseRESTAPI
from altaircms.models import DBSession
from altaircms.fanstatic import with_bootstrap, bootstrap_need
from altaircms.auth.errors import AuthenticationError
from altaircms.auth.forms import RoleForm
from .models import Operator, Role, Permission, RolePermission, DEFAULT_ROLE


@view_config(route_name='login', renderer='altaircms:templates/login.mako')
@view_config(context='pyramid.httpexceptions.HTTPForbidden', renderer='altaircms:templates/login.mako',
             decorator=with_bootstrap)
def login(request):
    message = ''
    return dict(
        message=message
    )


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)

    return HTTPFound(
        location=request.resource_url(request.context),
        headers=headers
    )


class OAuthLogin(object):
    client_id = "fa12a58972626f0597c2faee1454e1"
    secret_key = "c5f20843c65870fad8550e3ad1f868"
    def __init__(self, request,
                 authorize_url='http://localhost:7654/login/authorize',
                 access_token_url='http://localhost:7654/api/access_token',
                 _stub_client=None):
        self.request = request

        self.access_token_url = access_token_url
        self.authorize_url = authorize_url

        self._stub_client = _stub_client

    def _oauth_request(self, client, url, method):
        if self._stub_client:
            return self._stub_client.request(url, method)

        return client.request(url, method)

    @view_config(route_name='oauth_entry')
    def oauth_entry(self):
        return HTTPFound('%s?client_id=%s&response_type=code' %
                         (self.authorize_url, self.client_id))

    @view_config(route_name='oauth_callback')
    def oauth_callback(self):

        import urlparse
        import urllib

        data = None
        try:
            args = dict(
                client_id=self.client_id,
                client_secret=self.secret_key,
                code=self.request.GET.get("code"),
                grant_type='authorization_code')

            data = json.loads(urllib.urlopen(
                self.access_token_url +
                "?" + urllib.urlencode(args)).read())
        except IOError, e:
            print e

        print data

        try:
            operator = DBSession.query(Operator).filter_by(auth_source='oauth', user_id=data['user_id']).one()
            operator.last_login = datetime.now()
            DBSession.add(operator)
        except NoResultFound:
            role = DBSession.query(Role).filter_by(name=data.get('role', DEFAULT_ROLE)).one()
            operator = Operator(
                auth_source='oauth',
                user_id=data['user_id'],
                screen_name=data['screen_name'],
                oauth_token=data['access_token'],
                oauth_token_secret='',
                role_id=role.id
            )
            DBSession.add(operator)

        headers = remember(self.request, operator.user_id)
        transaction.commit()

        # url = self.request.route_path("dashboard")
        url = self.request.registry.settings.get('oauth.callback_success_url', '/')
        return HTTPFound(url, headers=headers)




"""
__all__ = [
    'login',
    'logout'
]

@view_config(name='login', renderer='altaircms:templates/login.mako')
@view_config(context='pyramid.httpexceptions.HTTPForbidden', renderer='altaircms:templates/login.mako')
def login(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url

    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from

    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''

    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if USERS.get(login) == password:
            headers = remember(request, login)
            return HTTPFound(location = came_from, headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        logged_in = authenticated_userid(request)
    )


@view_config(context='velruse.api.AuthenticationComplete', renderer='json')
def auth_complete_view(context, request):
    return {
        'profile': context.profile,
        'credentials': context.credentials,
        }


@view_config(context='velruse.exceptions.AuthenticationDenied', renderer='json')
def auth_denied_view(context, request):
    return context.args
"""


class OperatorView(object):
    def __init__(self, request):
        self.request = request
        self.id = request.matchdict.get('id', None)
        if self.id:
            self.operator = OperatorAPI(self.request, self.id).read()

        bootstrap_need()

    @view_config(route_name="operator_list", renderer='altaircms:templates/auth/operator/list.mako', permission="operator_read")
    def list(self):
        operators = OperatorAPI(self.request).read()

        return dict(
            operators=operators
        )

    @view_config(route_name="operator", renderer='altaircms:templates/auth/operator/view.mako', permission="operator_read")
    def read(self):
        self._check_obj()
        return dict(operator=self.operator)

    @view_config(route_name="operator", permission="operator_delete",
        request_method="POST", request_param="_method=delete")
    def delete(self):
        self._check_obj()
        logged_in_user_id = authenticated_userid(self.request)
        user_id = self.operator.user_id
        DBSession.delete(self.operator)

        if user_id == logged_in_user_id:
            return logout(self.request)

        # @TODO 何かしらのフラッシュメッセージ？みたいなのを送り込んで遷移先で表示する
        return HTTPFound(self.request.route_path("operator_list"))


    def _check_obj(self):
        if not self.operator:
            return HTTPNotFound()

class OperatorAPI(BaseRESTAPI):
    validationschema = None
    model = Operator


class RoleAPI(BaseRESTAPI):
    model = Role


class RoleView(object):
    def __init__(self, request):
        self.request = request
        self.id = request.matchdict.get('id', None)
        if self.id:
            self.role = RoleAPI(self.request, self.id).read()

        bootstrap_need()

    @view_config(route_name="role_list", request_method="GET", renderer="altaircms:templates/auth/role/list.mako")
    def list(self):
        return dict(
            roles=DBSession.query(Role)
        )

    @view_config(route_name="role", request_method="POST", renderer="altaircms:templates/auth/role/view.mako")
    @view_config(route_name="role", request_method="GET", renderer="altaircms:templates/auth/role/view.mako")
    def read(self):
        if self.request.method == "POST":
            form = RoleForm(self.request.POST)
            if form.validate():
                perm = Permission(id=form.data.get('permission'))
                DBSession.add(RolePermission(role_id=self.id, permission_id=perm.id))
                return HTTPFound(self.request.route_path('role', id=self.id))
        else:
            form = RoleForm()
        return dict(
            form=form,
            role=self.role
        )

    @view_config(route_name="role", request_method="POST", request_param="_method=delete")
    def delete(self):
        try:
            DBSession.delete(self.role)
        except:
            raise
        return HTTPFound(self.request.route_path("role_list"))


class RolePermissionAPI(BaseRESTAPI):
    model = RolePermission


class RolePermissionView(object):
    def __init__(self, request):
        self.request = request
        self.role_id = request.matchdict.get('role_id', None)
        self.role_permission_id = request.matchdict.get('id', None)
        if self.role_id:
            self.role = RoleAPI(self.request, self.role_id).read()
        if self.role_permission_id:
            self.role_permission = DBSession.query(RolePermission).filter_by(role_id=self.role_id, permission_id=self.role_permission_id).one()

        bootstrap_need()

    def create(self):
        pass

    @view_config(route_name='role_permission_list', request_method="GET")
    def read(self):
        return dict(
            permissions=DBSession.query(RolePermission)
        )

    def update(self):
        pass

    @view_config(route_name='role_permission', request_method="POST", request_param="_method=delete")
    def delete(self):
        try:
            DBSession.delete(self.role_permission)
        except:
            raise
        return HTTPFound(self.request.route_path("role", id=self.role.id))
