# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from beaker.cache import CacheManager, cache_regions

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import remember, forget
from pyramid.security import authenticated_userid
from pyramid.view import view_config, view_defaults

from altair.app.ticketing.core.models import *
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import merge_and_flush, record_to_multidict, merge_session_with_post
from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.operators import api as o_api
from altair.app.ticketing.views import BaseView

from .forms import SSLClientCertLoginForm, LoginForm, OperatorForm, ResetForm
from .utils import (
    get_auth_identifier_from_client_certified_request,
    AESEncryptor
)

@view_defaults(decorator=with_bootstrap, route_name='login.default', renderer='altair.app.ticketing:templates/login/default.html')
class DefaultLoginView(BaseView):
    def __init__(self, context, request):
        cache_manager = CacheManager(cache_regions=cache_regions)
        self.cache = cache_manager.get_cache_region(__name__, region='altair_login_locked_times_limiter')
        super(DefaultLoginView, self).__init__(context, request)

    @view_config(request_method='GET')
    def index_get(self):
        user_id = authenticated_userid(self.request)
        user = Operator.get_by_login_id(user_id)
        if user is not None:
            next_url = self.request.GET.get('next')
            return HTTPFound(location=next_url if next_url else self.request.route_path("index"))
        return {
            'form':LoginForm()
        }

    def _flash_locked_message(self):
        self.request.session.flash(u'入力されたユーザー名とパスワードが一定回数連続して一致しなかったため、ログインを制限させていただきました。')
        self.request.session.flash(u'セキュリティロックは30分後に解除いたします。')

    @view_config(request_method='POST')
    def index_post(self):
        form = LoginForm(self.request.POST)
        if form.validate():
            # 同じIDに対し、最初に間違えてから30分以内に３回連続で間違えたら30分間ログイン不可とする。
            # If the user is locked.
            login_id = form.data.get('login_id')
            login_count = self.cache.get(login_id, createfunc=lambda: 0)
            locked_count = int(self.request.registry.settings.get('altair.login.locked.count'))
            if login_count >= locked_count:
                self._flash_locked_message()
                return {
                    'form': form
                }

            operator = Operator.login(form.data.get('login_id'), form.data.get('password'))
            if operator is None:
                # If the user has already made 3 times errors. the user will be locked for a half hour.
                # count error times.
                self.cache.put(login_id, max(login_count + 1, 0))
                login_count = self.cache.get(login_id, createfunc=lambda: 0)
                if login_count >= locked_count:
                    self._flash_locked_message()
                else:
                    self.request.session.flash(u'ユーザー名またはパスワードが違います。')
                return {
                    'form': form
                }
            # remove all the login log.
            self.cache.remove_value(login_id)

            next_url = self.request.GET.get('next')

            if operator.is_first:
                aes = AESEncryptor()
                op_token = aes.get_token(operator.id)
                self.request.session.flash(u'初回ログインのため、パスワードを更新してください。')
                return HTTPFound(
                    location=self.request.route_path('login.info.edit', _query=dict(op_token=op_token, next=next_url)))


            merge_and_flush(operator)
            headers = remember(self.request, form.data.get('login_id'))
            return HTTPFound(location=next_url if next_url else self.request.route_path("index"), headers=headers)
        else:
            return {
                'form':form
            }

@view_defaults(decorator=with_bootstrap, route_name='login.client_cert', renderer='altair.app.ticketing:templates/login/client_cert.html')
class SSLClientCertLoginView(BaseView):
    @view_config(request_method='GET')
    def index_get(self):
        user_id = authenticated_userid(self.request)
        user = Operator.get_by_login_id(user_id)
        if user is not None:
            next_url = self.request.GET.get('next')
            return HTTPFound(location=next_url if next_url else self.request.route_path("index"))
        return {
            'form':SSLClientCertLoginForm()
        }

    @view_config(request_method='POST')
    def index_post(self):
        form = SSLClientCertLoginForm(self.request.POST)
        auth_identifier = get_auth_identifier_from_client_certified_request(self.request)
        if auth_identifier is None:
            self.request.session.flash(u'クライアント証明書が提示されていません')
            return {
                'form': form
                }
        if form.validate():
            operator = Operator.login(auth_identifier, form.data.get('password'))
            if operator is None:
                self.request.session.flash(u'パスワードが違います。')
                return {
                    'form':form
                    }
            merge_and_flush(operator)
            headers = remember(self.request, auth_identifier)
            next_url = self.request.GET.get('next')
            return HTTPFound(location=next_url if next_url else self.request.route_path("index"), headers=headers)
        else:
            return {
                'form':form
            }


@view_defaults(decorator=with_bootstrap, route_name='login.reset', renderer='altair.app.ticketing:templates/login/reset.html', permission='authenticated')
class LoginPasswordResetView(BaseView):
    @view_config(request_method='GET')
    def reset_get(self):
        return {
            'form':ResetForm()
        }

    @view_config(request_method='POST')
    def reset_post(self):
        f = ResetForm(self.request.POST)
        if f.validate():
            operator = Operator.get_by_email(f.data.get('email'))
            # TODO: operator.notify_reset_password()  # パスワード再設定URLをメール通知
            return HTTPFound(location=self.request.route_path('login.reset.complete'))
        else:
            return {
                'form':f
            }

    @view_config(route_name='login.reset.complete', renderer='altair.app.ticketing:templates/login/reset_complete.html', permission='authenticated')
    def reset_complete(self):
        return {}


def _get_operator(context, request):
    operator = context.user or None
    if not operator:
        op_token = request.GET.get('op_token', None)
        if op_token:
            operator_id = AESEncryptor.get_id_from_token(op_token)
            operator = Operator.filter_by(id=operator_id).first()
    return operator


@view_defaults(decorator=with_bootstrap)
class LoginUser(BaseView):
    @view_config(route_name='login.info', renderer='altair.app.ticketing:templates/login/info.html', permission='authenticated')
    def info(self):
        login_id = authenticated_userid(self.request)
        return {
            'operator':Operator.get_by_login_id(login_id),
            'form':OperatorForm(),
        }

    @view_config(route_name='login.info.edit', request_method="GET", renderer='altair.app.ticketing:templates/login/edit.html')
    def info_edit_get(self):
        action_url = self.request.current_route_path()
        operator = _get_operator(self.context, self.request)
        if not operator:
            return HTTPNotFound("Operator id %s is not found")

        f = OperatorForm()
        f.process(record_to_multidict(operator))
        f.login_id.data = operator.auth.login_id
        return {
            'form':f,
            'action_url': action_url
        }

    @view_config(route_name='login.info.edit', request_method="POST", renderer='altair.app.ticketing:templates/login/edit.html')
    def info_edit_post(self):
        action_url = self.request.current_route_path()
        next_url = self.request.GET.get('next')
        operator = _get_operator(self.context, self.request)
        if operator is None:
            return HTTPNotFound("Operator id %s is not found")

        f = OperatorForm(self.request.POST, request=self.request)

        if operator.is_first and not f.data['password']:
            self.request.session.flash(u'初回ログインのため、パスワードを更新してください。')
            return {
                'form': f,
                'action_url': action_url
            }

        if f.validate():
            if not f.data['password']:
                password = operator.auth.password
            else:
                password = o_api.crypt(f.data['password'])

            operator = merge_session_with_post(operator, f.data)
            operator.expire_at = datetime.today() + timedelta(days=180)
            operator.auth.login_id = f.data['login_id']
            operator.auth.password = password
            if operator.is_first:
                operator.status = 1

            operator.save()

            self.request.session.flash(u'ログイン情報を更新しました。')
            headers = remember(self.request, operator.auth.login_id)
            return HTTPFound(location=next_url if next_url else self.request.route_path('login.info'), headers=headers)
        else:
            return {
                'form':f,
                'action_url':action_url
            }

    @view_config(route_name='login.logout')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location=self.request.route_url('index'), headers=headers)
