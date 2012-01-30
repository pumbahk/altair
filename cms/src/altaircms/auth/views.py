# coding: utf-8
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid, forget, remember
from pyramid.view import view_config

from altaircms.security import USERS

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


@view_config(name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.resource_url(request.context), headers = headers)


@view_config(context='velruse.api.AuthenticationComplete', renderer='json')
def auth_complete_view(context, request):
    return {
        'profile': context.profile,
        'credentials': context.credentials,
        }


@view_config(context='velruse.exceptions.AuthenticationDenied',
    renderer='json')
def auth_denied_view(context, request):
    return context.args
