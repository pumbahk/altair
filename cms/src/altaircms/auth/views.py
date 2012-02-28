# coding: utf-8
import urlparse

from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPUnauthorized
from pyramid.security import forget, remember
from pyramid.view import view_config

from sqlalchemy.orm.exc import NoResultFound

import oauth2
import transaction

from altaircms.views import BaseRESTAPI
from altaircms.models import DBSession
from altaircms.fanstatic import with_bootstrap
from altaircms.auth.errors import AuthenticationError
from .models import Operator, Role, DEFAULT_ROLE


@view_config(name='login', renderer='altaircms:templates/login.mako')
@view_config(context='pyramid.httpexceptions.HTTPForbidden', renderer='altaircms:templates/login.mako',
             decorator=with_bootstrap)
def login(request):
    message = ''
    return dict(
        message=message
    )


@view_config(name='logout')
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

        return HTTPFound(location = '/', headers = headers)


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


class OperatorApi(BaseRESTAPI):
    validationschema = None
    model = Operator
