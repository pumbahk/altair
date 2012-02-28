# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import remember, forget
from hashlib import md5
from pyramid.url import route_path
from pyramid.security import authenticated_userid

from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush, session

from forms import LoginForm, OperatorForm
from ticketing.models import Client, Operator, OperatorRole, session

from deform.form import Form,Button
from deform.exception import ValidationFailure

import datetime

VERIFIER = 'verifier'

CALLBACK_URL = {
    'backend' : 'http://localhost:7654/admin/'
}

@view_config(route_name='login.index', renderer='ticketing:templates/login/index.html')
def index(context, request):
    user_id = authenticated_userid(request)
    user = Operator.get_by_login_id(user_id)
    if user is not None:
        return HTTPFound(location=CALLBACK_URL.get(request.GET.get('app_id', 'backend')))

    if 'submit' in request.POST:
        form = LoginForm(request.POST)
        if form.validate():
            data = form.data
            login_id = data.get('login_id')
            password = data.get('password')
            app_id = request.GET.get('app_id', 'backend')
            operator = session.query(Operator)\
                .filter(Operator.login_id == login_id and Operator.password == md5(password).hexdigest()).first()
            operator.auth_code = md5(password+login_id+str(datetime.date.today())).hexdigest()
            session.merge(operator)
            session.flush()

            if operator is None:
                return {
                    'form':form.render()
                }
            headers = remember(request, login_id)
            return HTTPFound(location=CALLBACK_URL.get(app_id if app_id is not None else 'backend') , headers=headers)

        else:
            return {
                'form':form
            }
    else:
        return {
            'form':LoginForm ()
        }

@view_config(route_name='login.info', renderer='ticketing:templates/login/info.html', permission='authenticated')
def info(context, request):
    login_id = authenticated_userid(request)
    return {'operator' : session.query(Operator).filter(Operator.login_id == login_id).first()}

@view_config(route_name='login.info.edit', renderer='ticketing:templates/login/edit.html', permission='authenticated')
def info_edit(context, request):
    login_id = authenticated_userid(request)
    operator = session.query(Operator).filter(Operator.login_id == login_id).first()
    if operator is None:
        return HTTPNotFound("Operator id %s is not found" % login_id)
    f = Form(
        OperatorForm(),
        buttons=(Button(name='submit',title=u'更新'),)
    )
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            data = f.validate(controls)
            record = merge_session_with_post(operator, data)
            record.secret_key = md5(record.secret_key).hexdigest()
            merge_and_flush(record)

            return HTTPFound(location=route_path('login.info', request))
        except ValidationFailure, e:
            return {'form':e.render()}
    else:
        appstruct = record_to_appstruct(operator)
        return {
            'form':f.render(appstruct=appstruct)
        }

@view_config(route_name='login.logout', renderer='ticketing:templates/login/info.html', permission='authenticated')
def logout(context, request):
    headers = forget(request)
    loc = request.route_url('login.index')
    return HTTPFound(location=loc, headers=headers)



