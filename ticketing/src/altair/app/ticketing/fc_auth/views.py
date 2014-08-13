# -*- coding:utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from altair.auth import who_api as get_who_api
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.mobile.api import is_mobile_request
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core import api as core_api
import altair.app.ticketing.users.models as u_m
from . import SESSION_KEY
from .api import do_authenticate

logger = logging.getLogger(__name__)

class LoginView(object):
    renderer_tmpl = "altair.app.ticketing.fc_auth:templates/{membership}/login.html"
    renderer_tmpl_mobile = "altair.app.ticketing.fc_auth:templates/{membership}/login_mobile.html"
    renderer_tmpl_smartphone = "altair.app.ticketing.fc_auth:templates/{membership}/login_smartphone.html"

    detail_renderer_tmpl = "altair.app.ticketing.fc_auth:templates/{membership}/{detail_membership}/login.html"
    detail_renderer_tmpl_mobile = "altair.app.ticketing.fc_auth:templates/{membership}/{detail_membership}/login_mobile.html"
    detail_renderer_tmpl_smartphone = "altair.app.ticketing.fc_auth:templates/{membership}/{detail_membership}/login_smartphone.html"

    def __init__(self, request):
        self.request = request
        self.context = request.context

    def select_renderer(self, membership, detail_membership=None):
        if detail_membership:
            if is_mobile_request(self.request):
                self.request.override_renderer = self.detail_renderer_tmpl_mobile.format(membership=membership, detail_membership=detail_membership)
            elif cart_api.is_smartphone(self.request):
                self.request.override_renderer = self.detail_renderer_tmpl_smartphone.format(membership=membership, detail_membership=detail_membership)
            else:
                self.request.override_renderer = self.detail_renderer_tmpl.format(membership=membership, detail_membership=detail_membership)
        else:
            if is_mobile_request(self.request):
                self.request.override_renderer = self.renderer_tmpl_mobile.format(membership=membership)
            elif cart_api.is_smartphone(self.request):
                self.request.override_renderer = self.renderer_tmpl_smartphone.format(membership=membership)
            else:
                self.request.override_renderer = self.renderer_tmpl.format(membership=membership)

    @property
    def return_to_url(self):
        return self.request.session.get(SESSION_KEY, {}).get('return_url') or core_api.get_host_base_url(self.request)

    @view_config(request_method="GET", route_name='fc_auth.login', renderer='json', http_cache=60)
    @view_config(request_method="GET", route_name='fc_auth.detail_login', renderer='json', http_cache=60)
    def login_form(self):
        membership = self.request.matchdict['membership']
        detail_membership = self.request.matchdict.get('detail_membership', None)
        self.select_renderer(membership, detail_membership)
        return dict(username='')

    @view_config(request_method="POST", route_name='fc_auth.login', renderer='string')
    @view_config(request_method="POST", route_name='fc_auth.detail_login', renderer='string')
    def login(self):
        who_api = get_who_api(self.request, "fc_auth")
        authmembership = membership = self.request.matchdict['membership']
        detail_membership = self.request.matchdict.get('detail_membership', None)
        if detail_membership:
            authmembership = detail_membership
        username = self.request.params['username']
        password = self.request.params['password']
        logger.debug("authenticate for membership %s" % authmembership)

        authenticated = None
        headers = None
        identity = None

        result = do_authenticate(self.request, authmembership, username, password)
        if result is not None:
            # result には user_id が含まれているが、これを identity とすべきかは
            # 議論の余地がある。user_id を identity にしてしまえば DB 負荷を
            # かなり減らすことができるだろう。
            identity = {
                'membership': authmembership,
                'username': username,
                }

        if identity is not None:
            authenticated, headers = who_api.login(identity)

        if authenticated is None:
            self.select_renderer(membership, detail_membership)
            return {'username': username,
                    'message': u'IDかパスワードが一致しません'}

        return_to_url = self.return_to_url 
        res = HTTPFound(location=return_to_url, headers=headers)
        return res

    @view_config(request_method="POST", route_name='fc_auth.guest', renderer='string')
    @view_config(request_method="POST", route_name='fc_auth.detail_guest', renderer='string')
    def guest_login(self):
        who_api = get_who_api(self.request, "fc_auth")
        authmembership = membership = self.request.matchdict['membership']
        detail_membership = self.request.matchdict.get('detail_membership', None)
        if detail_membership:
            authmembership = detail_membership
        logger.debug("guest authenticate for membership %s" % authmembership)

        identity = {
            'membership': authmembership,
            'is_guest': True,
        }
        authenticated, headers = who_api.login(identity)

        if authenticated is None:
            self.select_renderer(membership, detail_membership)
            return {'username': '',
                    'guest_message': u''}

        return_to_url = self.return_to_url
        res = HTTPFound(location=return_to_url, headers=headers)

        return res

