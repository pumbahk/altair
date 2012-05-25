from pyramid.view import view_config, view_defaults
from ticketing.views import BaseView
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound, HTTPError

from pyramid.url import route_path
from pyramid.security import authenticated_userid

from ticketing.oauth2.models import Service, AccessToken
#from forms import AuthorizeForm
from ticketing.oauth2.authorize import Authorizer, MissingRedirectURI, AuthorizationException
from ticketing.operators.models import Operator

import sqlahelper
session = sqlahelper.get_session()

@view_config(route_name='api.access_token' , renderer='json')
def access_token(context, request):
    client = Service.get_key(request.GET.get("client_id"))
    token = AccessToken.get_by_key(request.GET.get("code"))

    if token and client:
        operator = token.operator
        return {
            'access_token'  : token.token,
            'user_id'       : operator.id,
            'role'          : operator.roles[0].name,
            'client_id'     : operator.organization.id,
            'client_name'   : operator.organization.name,
            'screen_name'   : operator.name,
        }
    else:
        return {}


# TODO move to oauth2
@view_defaults(permission='authenticated')
class LoginOAuth(BaseView):

    @view_config(route_name='login.authorize')
    def authorize(self):
        login_id = authenticated_userid(self.request)
        operator = Operator.get_by_login_id(login_id)

        user = self.context.user
        authorizer = Authorizer()

        try:
            authorizer.validate(self.request, self.context)
        except MissingRedirectURI, e:
            return HTTPFound(location=self.request.route_url("login.missing_redirect_url"))
        except AuthorizationException, e:
            return authorizer.error_redirect()

        if self.request.method == 'GET':
            if user:
                return authorizer.grant_redirect()
            else:
                return HTTPError()

        return HTTPFound(location="/")
