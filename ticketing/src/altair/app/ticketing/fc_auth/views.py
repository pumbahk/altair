# -*- coding:utf-8 -*-
import re
import logging
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults
from pyramid.decorator import reify
from urlparse import urlparse
from altair.auth.api import get_auth_api, get_plugin_registry
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.mobile.api import is_mobile_request
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core import api as core_api
import altair.app.ticketing.users.models as u_m
from . import SESSION_KEY
from .api import do_authenticate
from .rendering import overridable_renderer
from .resources import FCAuthResource, FixedMembershipFCAuthResource

logger = logging.getLogger(__name__)

def return_to_url(request):
    passed_return_to_url = request.params.get('return_to')
    if passed_return_to_url is not None:
        parsed_passed_return_to_url = urlparse(passed_return_to_url)
        if (not parsed_passed_return_to_url.scheme and not parsed_passed_return_to_url.netloc) \
           or parsed_passed_return_to_url.netloc == request.host:
            return passed_return_to_url
    return request.session.get(SESSION_KEY, {}).get('return_url') or core_api.get_host_base_url(request)

class FCAuthLoginViewMixin(object):
    @property
    def auth_api(self):
        return get_auth_api(self.request)

    @reify
    def plugin(self):
        return get_plugin_registry(self.request).lookup('fc_auth')

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
            identities, auth_factors, metadata = self.auth_api.login(self.request, self.request.response, credentials, auth_factor_provider_name=self.plugin.name)

        if identities is None:
            if self.request.context.membership.enable_login_body:
                membership_info = self.request.context.membership
                change_message = u'<input type="hidden">'
                pc_smartphone_error_message = u'<span class="red">' + membership_info.login_body_error_message + u'</span>'
                mobile_error_message = u'<span style="color: red">' + membership_info.login_body_error_message + u'</span>'
                if ISmartphoneRequest.providedBy(self.request):
                    self.request.context.membership.login_body_smartphone = \
                        re.sub(change_message, pc_smartphone_error_message, membership_info.login_body_smartphone)
                elif IMobileRequest.providedBy(self.request):
                    self.request.context.membership.login_body_mobile = \
                        re.sub(change_message, mobile_error_message, membership_info.login_body_mobile)
                else:
                    self.request.context.membership.login_body_pc = \
                        re.sub(change_message, pc_smartphone_error_message, membership_info.login_body_pc)

            return {'username': username,
                    'message': u'IDかパスワードが一致しません'}
        return HTTPFound(location=return_to_url(self.request), headers=self.request.response.headers)
   
    def do_guest_login(self, membership):
        logger.debug("guest authenticate for membership %s" % membership)

        credentials = {
            'membership': membership,
            'is_guest': True,
            }
        identities, auth_factors, metadata = self.auth_api.login(self.request, self.request.response, credentials, auth_factor_provider_name=self.plugin.name)

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
