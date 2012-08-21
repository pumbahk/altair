import logging
from pyramid.httpexceptions import HTTPFound
from repoze.who.api import get_api as get_who_api
from pyramid.view import view_config

logger = logging.getLogger(__name__)

class LoginView(object):
    renderer_tmpl = "ticketing.cart.fc_auth:templates/{membership}/login.html"

    def __init__(self, request):
        self.request = request
        self.context = request.context


    def select_renderer(self, membership):
        self.request.override_renderer = self.renderer_tmpl.format(membership=membership)

    @property
    def return_to_url(self):
        environ  = self.request.environ
        session = environ['session.rakuten_openid']
        return session.get('return_url')

    @view_config(request_method="GET", route_name='fc_auth.login', renderer='json')
    def login_form(self):
        membership = self.request.matchdict['membership']
        self.select_renderer(membership)
        return dict(username='')


    @view_config(request_method="POST", route_name='fc_auth.login', renderer='string')
    def login(self):
        who_api = get_who_api(self.request.environ)
        membership = self.request.matchdict['membership']
        username = self.request.params['username']
        password = self.request.params['password']
        logger.debug("authenticate for membership %s" % membership)

        identity = {
            'membership': membership,
            'username': username,
            'password': password,
        }
        authenticated, headers = who_api.login(identity)

        if authenticated is None:
            self.select_renderer(membership)
            return {'username': username}


        return_to_url = self.return_to_url
        res = HTTPFound(location=return_to_url, headers=headers)


        return res

