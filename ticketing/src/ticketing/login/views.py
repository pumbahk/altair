# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import remember, forget

from pyramid.url import route_path
from pyramid.security import authenticated_userid

from forms import LoginForm, OperatorForm, ResetForm
from ticketing.models import *
from ticketing.views import BaseView
from ticketing.operators.models import Operator

from ticketing.fanstatic import with_bootstrap

import sqlahelper
session = sqlahelper.get_session()

from hashlib import md5

@view_defaults(decorator=with_bootstrap)
class Login(BaseView):

    @view_config(route_name='login.index', request_method="GET", renderer='ticketing:templates/login/index.html')
    def index_get(self):
        user_id = authenticated_userid(self.request)
        user = Operator.get_by_login_id(user_id)
        if user is not None:
            return HTTPFound(location=route_path("index", self.request))
        return {
            'form':LoginForm ()
        }

    @view_config(route_name='login.index', request_method="POST", renderer='ticketing:templates/login/index.html')
    def index_post(self):
        form = LoginForm(self.request.POST)
        if form.validate():
            data = form.data
            operator = Operator.login(data.get("login_id"), data.get("password"))
            if operator is None:
                form.login_id.errors.append(u"ユーザー名またはパスワードが違います。")
                return {
                    'form':form
                }
            merge_and_flush(operator)
            headers = remember(self.request, data.get("login_id"))
            next_url = self.request.GET.get('next')
            return HTTPFound(location=next_url if next_url is None else route_path("index", self.request), headers=headers)
        else:
            return {
                'form':form
            }

    @view_config(route_name='login.reset', request_method="GET", renderer='ticketing:templates/login/reset.html')
    def reset(self):
        form = ResetForm()
        return {
            'form' : form
        }

    @view_config(route_name='login.reset', request_method="POST", renderer='ticketing:templates/login/reset_commit.html')
    def reset(self):
        form = ResetForm()
        if form.validate():
            data = form.data
            operator = Operator.get_by_email(data.get("email"))
            if operator:
                pass
        else:
            return {
                'form':form
            }

@view_defaults(decorator=with_bootstrap, permission='authenticated')
class LoginUser(BaseView):

    @view_config(route_name='login.info', renderer='ticketing:templates/login/info.html')
    def info(self):
        login_id = authenticated_userid(self.request)
        return {'operator' : session.query(Operator).filter(Operator.login_id == login_id).first()}

    @view_config(route_name='login.info.edit', request_method="GET", renderer='ticketing:templates/login/_form.html')
    def info_edit_get(self):
        operator = self.context.user
        if operator is None:
            return HTTPNotFound("Operator id %s is not found")
        appstruct = record_to_multidict(operator)
        f = OperatorForm()
        f.process(appstruct)
        return {
            'form':f
        }

    @view_config(route_name='login.info.edit', request_method="POST", renderer='ticketing:templates/login/_form.html')
    def info_edit_post(self):
        operator = self.context.user
        if operator is None:
            return HTTPNotFound("Operator id %s is not found")

        f = OperatorForm(self.request.POST)
        if f.validate():
            data = f.data
            if not data['password']:
                del  data['password']
            record = merge_session_with_post(operator, data)
            record.secret_key = md5(record.secret_key).hexdigest()
            merge_and_flush(record)
            return HTTPFound(location=route_path("login.info", self.request))
        else:
            return {'form':f }


    @view_config(route_name='login.logout', renderer='ticketing:templates/login/info.html')
    def logout(self):
        headers = forget(self.request)
        loc = self.request.route_url('login.index')
        return HTTPFound(location=loc, headers=headers)






