from pyramid.view import view_config, view_defaults
from ticketing.views import BaseView

from ticketing.oauth2.models import Service, AccessToken

@view_config(route_name='api.access_token' , renderer='json')
def access_token(context, request):
    client = Service.get_key(request.GET.get("client_id"))
    token = AccessToken.get_by_key(request.GET.get("code"))

    if token and client:
        operator = token.operator
        print operator
        return {
            'access_token'  : token.token,
            'user_id'       : operator.id,
            'client_id'     : operator.client.id,
            'client_name'   : operator.client.name,
            'screen_name'   : operator.name,
        }
    else:
        return {}


# TODO move to oauth2
@view_defaults(permission='authenticated')
class LoginOAuth(BaseView):

    def _authorize(self, authorizer, form=None):
        if form is None:
            form = AuthorizeForm()
        return render_to_response(
            'ticketing:templates/login/authorize.html',
            {
                'form'          : form,
                "authorizer"    : authorizer,
                'form_action'   : route_path('login.authorize',self.request, _query_string=authorizer.query_string)
            },
            request=self.request)

    @view_config(route_name='login.authorize', permission='authenticated')
    def authorize(self):

        login_id = authenticated_userid(self.request)
        operator = session.query(Operator).filter(Operator.login_id == login_id).first()

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
                return self._authorize(authorizer)

        return HTTPFound(location="/")