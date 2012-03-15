# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import remember, forget

from pyramid.url import route_path
from pyramid.security import authenticated_userid
from ticketing.oauth2.authorize import Authorizer, MissingRedirectURI, AuthorizationException

from forms import LoginForm, OperatorForm, AuthorizeForm
from ticketing.models import *

from ticketing.fanstatic import with_bootstrap
from ticketing.fanstatic import bootstrap_need

@view_config(route_name='login.index', renderer='ticketing:templates/login/index.html', decorator=with_bootstrap)
def index(context, request):
    user_id = authenticated_userid(request)
    user = Operator.get_by_login_id(user_id)
    if user is not None:
        return HTTPFound(location=route_path("index", request))

    if 'submit' in request.POST:
        form = LoginForm(request.POST)
        if form.validate():
            data = form.data
            operator = Operator.login(data.get("login_id"), data.get("password"))
            if operator is None:
                return {
                    'form':form
                }
            merge_and_flush(operator)
            headers = remember(request, data.get("login_id"))
            next_url = request.GET.get('next')
            return HTTPFound(location=next_url if next_url else route_path("index", request), headers=headers)
        else:
            return {
                'form':form
            }
    else:
        return {
            'form':LoginForm ()
        }

@view_config(route_name='login.info', renderer='ticketing:templates/login/info.html', permission='authenticated', decorator=with_bootstrap)
def info(context, request):
    login_id = authenticated_userid(request)
    return {'operator' : session.query(Operator).filter(Operator.login_id == login_id).first()}

@view_config(route_name='login.info.edit', renderer='ticketing:templates/login/edit.html', permission='authenticated', decorator=with_bootstrap)
def info_edit(context, request):
    operator = context.user
    if operator is None:
        return HTTPNotFound("Operator id %s is not found" % login_id)
    f = OperatorForm(request.POST)
    if 'submit' in request.POST:
        if f.validate():
            data = f.data
            if not data['password']:
                del  data['password']
            record = merge_session_with_post(operator, data)
            record.secret_key = md5(record.secret_key).hexdigest()
            merge_and_flush(record)
            return HTTPFound(location=route_path("login.info", request))
        else:
            return {'form':f }
    else:
        appstruct = record_to_multidict(operator)
        f.process(appstruct)
        return {
            'form':f
        }

@view_config(route_name='login.logout', renderer='ticketing:templates/login/info.html', permission='authenticated')
def logout(context, request):
    headers = forget(request)
    loc = request.route_url('login.index')
    return HTTPFound(location=loc, headers=headers)


def _authorize(request, authorizer, form=None):
    if form is None:
        form = AuthorizeForm()
    return render_to_response(
        'ticketing:templates/login/authorize.html',
        {
            'form'          : form,
            "authorizer"    : authorizer,
            'form_action'   : route_path('login.authorize',request, _query_string=authorizer.query_string)
        },
        request=request)

@view_config(route_name='login.authorize', permission='authenticated')
def authorize(context, request):

    login_id = authenticated_userid(request)
    operator = session.query(Operator).filter(Operator.login_id == login_id).first()

    user = context.user
    authorizer = Authorizer()

    try:
        authorizer.validate(request, context)
    except MissingRedirectURI, e:
        return HTTPFound(location=request.route_url("login.missing_redirect_url"))
    except AuthorizationException, e:
        return authorizer.error_redirect()

    if request.method == 'GET':
        if user:
            return authorizer.grant_redirect()
        else:
            return _authorize(request, authorizer)

    return HTTPFound(location="/")


