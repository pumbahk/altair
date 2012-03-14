# coding: utf-8
from datetime import datetime
import urlparse

from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPUnauthorized, HTTPNotFound
from pyramid.security import forget, remember, authenticated_userid
from pyramid.view import view_config

from sqlalchemy.orm.exc import NoResultFound

import oauth2
import transaction

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
    def __init__(self, request, consumer_key=None, consumer_secret=None,
                 authorize_url='http://twitter.com/oauth/authorize',
                 request_token_url='http://twitter.com/oauth/request_token',
                 access_token_url='http://twitter.com/oauth/access_token',
                 _stub_client=None):
        self.request = request

        self.api_endpoint = 'https://api.twitter.com/1/'

        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorize_url = authorize_url

        consumer_key = consumer_key if consumer_key else request.registry.settings['oauth.consumer_key']
        consumer_secret = consumer_secret if consumer_secret else request.registry.settings['oauth.consumer_secret']
        self.consumer = oauth2.Consumer(consumer_key, consumer_secret)

        self._stub_client = _stub_client

    def _oauth_request(self, client, url, method):
        if self._stub_client:
            return self._stub_client.request(url, method)

        return client.request(url, method)

    @view_config(route_name='oauth_entry')
    def oauth_entry(self):
        client = oauth2.Client(self.consumer)

        resp, content = self._oauth_request(client, self.request_token_url, "GET")
        if resp.status != 200 and resp.status != 302:
            return HTTPUnauthorized()

        request_token = dict(urlparse.parse_qsl(content))
        self.request.session['request_token'] = {
            'oauth_token': request_token['oauth_token'],
            'oauth_token_secret': request_token['oauth_token_secret']
        }
        return HTTPFound('%s?oauth_token=%s' % (self.authorize_url, request_token['oauth_token']))

    @view_config(route_name='oauth_callback')
    def oauth_callback(self):
        try:
            token = oauth2.Token(self.request.session['request_token']['oauth_token'],
                self.request.session['request_token']['oauth_token_secret'])
            client = oauth2.Client(self.consumer, token)

            resp, content = self._oauth_request(client, self.access_token_url, "GET")
            data = dict(urlparse.parse_qsl(content))

            if resp.status != 200 or 'user_id' not in data:
                raise AuthenticationError(resp.reason)
        except KeyError, e:
            return Forbidden('%s is not found' % (str(e), ))
        except AuthenticationError, e:
            return Forbidden(str(e))

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
                oauth_token=data['oauth_token'],
                oauth_token_secret=data['oauth_token_secret'],
                role_id=role.id
            )
            DBSession.add(operator)

        headers = remember(self.request, operator.user_id)

        del self.request.session['request_token']

        transaction.commit()

        # url = self.request.route_url("dashboard")
        url = self.request.registry.settings.get('oauth.callback_success_url', '/')
        return HTTPFound(url, headers=headers)


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
        return HTTPFound(self.request.route_url("operator_list"))


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
                return HTTPFound(self.request.route_url('role', id=self.id))
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
        return HTTPFound(self.request.route_url("role_list"))


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
        return HTTPFound(self.request.route_url("role", id=self.role.id))
