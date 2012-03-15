from pyramid.view import view_config

from ticketing.models.boxoffice import *

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
