# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime, timedelta

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import remember, forget
from pyramid.url import route_path
from pyramid.security import authenticated_userid

from ticketing.models import merge_and_flush, record_to_multidict, merge_session_with_post
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import *
from ticketing.operators.models import Operator
from ticketing.login.forms import LoginForm, OperatorForm, ResetForm

@view_defaults(decorator=with_bootstrap)
class Login(BaseView):

    @view_config(route_name='login.index', request_method='GET', renderer='ticketing:templates/login/index.html')
    def index_get(self):
        user_id = authenticated_userid(self.request)
        user = Operator.get_by_login_id(user_id)
        if user is not None:
            return HTTPFound(location=route_path('index', self.request))
        return {
            'form':LoginForm()
        }

    @view_config(route_name='login.index', request_method='POST', renderer='ticketing:templates/login/index.html')
    def index_post(self):
        form = LoginForm(self.request.POST)
        if form.validate():
            operator = Operator.login(form.data.get('login_id'), form.data.get('password'))
            if operator is None:
                form.login_id.errors.append(u'ユーザー名またはパスワードが違います。')
                return {
                    'form':form
                }
            merge_and_flush(operator)
            headers = remember(self.request, form.data.get('login_id'))
            next_url = self.request.GET.get('next')
            return HTTPFound(location=next_url if next_url else route_path("index", self.request), headers=headers)
        else:
            return {
                'form':form
            }

    @view_config(route_name='login.reset', request_method='GET', renderer='ticketing:templates/login/reset.html')
    def reset_get(self):
        return {
            'form':ResetForm()
        }

    @view_config(route_name='login.reset', request_method='POST', renderer='ticketing:templates/login/reset.html')
    def reset_post(self):
        f = ResetForm(self.request.POST)
        if f.validate():
            operator = Operator.get_by_email(f.data.get('email'))
            # TODO: operator.notify_reset_password()  # パスワード再設定URLをメール通知
            return HTTPFound(location=route_path('login.reset.complete', self.request))
        else:
            return {
                'form':f
            }

    @view_config(route_name='login.reset.complete', renderer='ticketing:templates/login/reset_complete.html')
    def reset_complete(self):
        return {}


@view_defaults(decorator=with_bootstrap, permission='authenticated')
class LoginUser(BaseView):

    @view_config(route_name='login.info', renderer='ticketing:templates/login/info.html')
    def info(self):
        login_id = authenticated_userid(self.request)
        return {
            'operator':Operator.get_by_login_id(login_id),
            'form':OperatorForm(),
        }

    @view_config(route_name='login.info.edit', request_method="GET", renderer='ticketing:templates/login/edit.html')
    def info_edit_get(self):
        operator = self.context.user
        if operator is None:
            return HTTPNotFound("Operator id %s is not found")

        f = OperatorForm()
        f.process(record_to_multidict(operator))
        f.login_id.data = operator.auth.login_id
        return {
            'form':f
        }

    @view_config(route_name='login.info.edit', request_method="POST", renderer='ticketing:templates/login/edit.html')
    def info_edit_post(self):
        operator = self.context.user
        if operator is None:
            return HTTPNotFound("Operator id %s is not found")

        f = OperatorForm(self.request.POST)
        if f.validate():
            if not f.data['password']:
                password = operator.auth.password
            else:
                password = hashlib.md5(f.data['password']).hexdigest()

            operator = merge_session_with_post(operator, f.data)
            operator.expire_at = datetime.today() + timedelta(days=180)
            operator.auth.login_id = f.data['login_id']
            operator.auth.password = password
            operator.save()

            self.request.session.flash(u'ログイン情報を更新しました')
            headers = remember(self.request, operator.auth.login_id)
            return HTTPFound(location=route_path('login.info', self.request), headers=headers)
        else:
            return {
                'form':f
            }

    @view_config(route_name='login.logout')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location=self.request.route_url('login.index'), headers=headers)
