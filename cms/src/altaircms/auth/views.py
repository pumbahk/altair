# coding: utf-8
import logging
from datetime import datetime
import urllib
import urllib2


from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import forget, remember, authenticated_userid
from pyramid.view import view_config
from pyramid.view import view_defaults

from sqlalchemy.orm.exc import NoResultFound

import json

from altaircms.lib.apiview import BaseRESTAPI
from altaircms.models import DBSession
from altaircms.lib.fanstatic_decorator import with_bootstrap
from altaircms.auth.forms import RoleForm
from .models import Operator, Role, DEFAULT_ROLE

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

    # def _oauth_request(self, client, url, method):
    #     if self._stub_client:
    #         return self._stub_client.request(url, method)

    #     return client.request(url, method)

    @view_config(route_name='oauth_entry')
    def oauth_entry(self):
        return HTTPFound('%s?client_id=%s&response_type=code' %
                         (self.authorize_url, self.client_id))

    def _create_oauth_model(self, role, data):
        return Operator(
                auth_source='oauth',
                user_id=data['user_id'],
                screen_name=data['screen_name'],
                oauth_token=data['access_token'],
                oauth_token_secret='',
                role=role,
            )
        
    @view_config(route_name='oauth_callback')
    def oauth_callback(self):

        data = None
        try:
            args = dict(
                client_id=self.client_id,
                client_secret=self.secret_key,
                code=self.request.GET.get("code"),
                grant_type='authorization_code')
            data = json.loads(urllib2.urlopen(
                self.access_token_url +
                "?" + urllib.urlencode(args)).read())
        except IOError, e:
            logging.exception(e)
            self.request.response.body = str(e)
            return self.request.response

        try:
            operator = Operator.query.filter_by(auth_source='oauth', user_id=data['user_id']).one()
            operator.last_login = datetime.now()
        except NoResultFound:
            logging.info("operator is not found. create it")

            role = Role.query.filter_by(name=data.get('role', DEFAULT_ROLE)).one()
            operator = self._create_oauth_model(role, data)
            DBSession.add(operator)

        headers = remember(self.request, operator.user_id)

        url = self.request.route_url('dashboard')
        return HTTPFound(url, headers=headers)




@view_defaults(decorator=with_bootstrap)
class OperatorView(object):
    def __init__(self, request):
        self.request = request
        self.id = request.matchdict.get('id', None)
        if self.id:
            self.operator = Operator.query.filter_by(id=self.id).one()

    @view_config(route_name="operator_list", renderer='altaircms:templates/auth/operator/list.mako', permission="operator_read")
    def list(self):
        operators = Operator.query.all()

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




class RolePermissionView(object):
    def __init__(self, request):
        self.request = request

    def create(self):
        pass

    @view_config(route_name='role_permission_list', request_method="GET", renderer="string") # deprecated? とりあえず string rendererつけとく
    def read(self):
        return dict(
            permissions=DBSession.query(RolePermission)
        )

    def update(self):
        pass

    @view_config(route_name='role_permission', request_method="POST", request_param="_method=delete")
    def delete(self):
        permission = self.request.matchdict.get('id')
        role_id = self.request.matchdict.get('role_id', None)
        role = Role.query.filter_by(id=role_id).one()
        if permission in role.permissions:
            role.permissions.remove(permission)
        
        return HTTPFound(self.request.route_path("role", id=role_id))
