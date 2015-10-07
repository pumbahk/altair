# -*- coding:utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults
from urlparse import urlparse
from altair.auth.api import get_auth_api
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.mobile.api import is_mobile_request
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core import api as core_api
import altair.app.ticketing.users.models as u_m
from . import SESSION_KEY
from .api import do_authenticate
from .rendering import overridable_renderer
from .resources import FCAuthResource, FixedMembershipFCAuthResource
from .events import Authenticated

logger = logging.getLogger(__name__)

def return_to_url(request):
    passed_return_to_url = request.params.get('return_to')
    if passed_return_to_url is not None:
        return urlparse(passed_return_to_url).path
    else:
        return request.session.get(SESSION_KEY, {}).get('return_url') or core_api.get_host_base_url(request)

class FCAuthLoginViewMixin(object):
    @property
    def auth_api(self):
        return get_auth_api(self.request)

    def do_login(self, membership):
        username = self.request.POST['username']
        password = self.request.POST['password']
        logger.debug("authenticate for membership %s" % membership)

        authenticated = None
        headers = None
        credentials = None

        result = do_authenticate(self.request, membership, username, password)
        if result is not None:
            credentials = {
                'membership': membership,
                'username': username,
                }

        identities = None
        if credentials is not None:
            identities, auth_factors, metadata = self.auth_api.login(self.request, self.request.response, credentials, auth_factor_provider_name='fc_auth')

        if identities is None:
            return {'username': username,
                    'message': u'IDかパスワードが一致しません'}

        self.request.registry.notify(
            Authenticated(
                self.request,
                membership,
                username,
                None
                )
            )
        return HTTPFound(location=return_to_url(self.request), headers=self.request.response.headers)
   
    def do_guest_login(self, membership):
        logger.debug("guest authenticate for membership %s" % membership)

        credentials = {
            'membership': membership,
            'is_guest': True,
            }
        identities, auth_factors, metadata = self.auth_api.login(self.request, self.request.response, credentials, auth_factor_provider_name='fc_auth')

        if identities is None:
            return {'username': '',
                    'guest_message': u''}

        return HTTPFound(location=return_to_url(self.request), headers=self.request.response.headers)

@view_defaults(context=FixedMembershipFCAuthResource, renderer=overridable_renderer('login.html'))
class FixedMembershipLoginView(FCAuthLoginViewMixin):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='fc_auth.login', request_method="GET", http_cache=60)
    def login_form(self):
        return dict(username='')

    @lbr_view_config(route_name='fc_auth.login', request_method="POST")
    def login(self):
        return self.do_login(self.context.membership.name)

    @lbr_view_config(route_name='fc_auth.guest', request_method="POST")
    def guest_login(self):
        return self.do_guest_login(self.context.membership.name)


@view_defaults(context=FCAuthResource, renderer=overridable_renderer('login.html'))
class LoginView(FCAuthLoginViewMixin):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='fc_auth.login', request_method="GET", http_cache=60)
    def login_form(self):
        return dict(username='')

    @lbr_view_config(route_name='fc_auth.login', request_method="POST")
    def login(self):
        membership_name = self.request.POST.get('membership')
        if membership_name is not None:
            membership = self.context.lookup_membership(membership_name)
        else:
            membership = self.context.primary_membership
        return self.do_login(membership.name)

    @lbr_view_config(route_name='fc_auth.guest', request_method="POST")
    def guest_login(self):
        membership_name = self.request.POST.get('membership')
        if membership_name is not None:
            membership = self.context.lookup_membership(membership_name)
        else:
            membership = self.context.primary_membership
        return self.do_guest_login(membership.name)
