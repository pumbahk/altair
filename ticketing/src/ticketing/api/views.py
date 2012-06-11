import logging
logger = logging.getLogger(__file__)

from pyramid.view import view_config, view_defaults
from ticketing.views import BaseView
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound, HTTPError

from pyramid.url import route_path
from pyramid.security import authenticated_userid, forget

from ticketing.oauth2.models import Service, AccessToken
#from forms import AuthorizeForm
from ticketing.oauth2.authorize import Authorizer, MissingRedirectURI, AuthorizationException
from ticketing.operators.models import Operator

import sqlahelper
session = sqlahelper.get_session()

@view_config(route_name='api.access_token' , renderer='json')
def access_token(context, request):
    service_key = request.GET.get("client_id")
    token_key = request.GET.get("code")

    logger.info("*api login* get api access token: service_key: %s, token_key: %s" % (service_key, token_key))

    client = Service.get_key(service_key)
    token = AccessToken.get_by_key(token_key)

    if token and client:
        operator = token.operator
        params = {
            'access_token'  : token.token,
            'user_id'       : operator.id,
            'roles'         : [role.name for role in operator.roles],
            'client_id'     : operator.organization.id,
            'client_name'   : operator.organization.name,
            'screen_name'   : operator.name,
        }
        logger.info("*api login* return api access token: %s" % params)
        return params
    else:
        return {}

@view_config(route_name="api.forget_loggedin")
def forget_loggedin(request):
    ## todo: added default failback.
    ## todo: need some validation.
    return_url = request.params.get("return_to", "/default-fail-back-path")
    logger.info("*api logout* logout from external site. return to: %s" % return_url)
    headers = forget(request)
    return HTTPFound(location=return_url, headers=headers)

# TODO move to oauth2
@view_defaults(permission='authenticated')
class LoginOAuth(BaseView):

    @view_config(route_name='login.authorize')
    def authorize(self):
        login_id = authenticated_userid(self.request)
        operator = Operator.get_by_login_id(login_id)

        user = self.context.user
        authorizer = Authorizer()

        logger.info("*api login* authorize request params %s" % dict(self.request.params))

        try:
            authorizer.validate(self.request, self.context)
        except MissingRedirectURI, e:
            return HTTPFound(location=self.request.route_url("login.missing_redirect_url"))
        except AuthorizationException, e:
            return authorizer.error_redirect()

        redirect_url = None
        if self.request.method == 'GET':
            if user:
                redirect_url = authorizer.grant_redirect()
            else:
                redirect_url = HTTPError()
        else:
            redirect_url = HTTPFound(location="/")
        logger.info("*api login* authorize redirect url: status:%s location:%s" % (redirect_url.status, redirect_url.location))
        return redirect_url
