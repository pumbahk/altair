# encoding: utf-8

import logging
import json
from datetime import datetime, timedelta
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.response import Response
from pyramid.decorator import reify
from pyramid.renderers import render_to_response
from webob.multidict import MultiDict
from webhelpers import paginate
from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.famiport.communication.exceptions import FamiEncodeError
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from ..models import (
    FamiPortPerformance,
    FamiPortReceipt,
    FamiPortEvent,
    FamiPortOrder,
    FamiPortOrderType,
    FamiPortReceiptType,
    FamiPortRefundEntry
)
from ..internal_api import make_suborder_by_order_no, mark_order_reissueable_by_order_no
from ..communication.api import get_ticket_preview_pictures
from ..exc import FamiPortAPIError
from .api import (
    lookup_user_by_credentials,
    lookup_performance_by_searchform_data,
    lookup_refund_performance_by_searchform_data,
    lookup_receipt_by_searchform_data,
    search_refund_ticket_by,
    encrypt_password,
    lookup_user_by_id,
    lookup_user_by_username
)
from .forms import (
    LoginForm,
    SearchPerformanceForm,
    SearchReceiptForm,
    RebookOrderForm,
    SearchRefundPerformanceForm,
    RefundTicketSearchForm,
    ChangePassWordForm,
    ReminderChangePassWordForm,
    PasswordReminderForm
)
from .utils import (
    validate_rebook_cond,
    validate_reprint_cond,
    AESEncryptor,
    sendmail
)
from .helpers import (
    ViewHelpers,
    get_paginator,
    RefundTicketSearchHelper,
)

from .models import FamiPortOperator

logger = logging.getLogger(__name__)

def flash_error_message(request, errors):
    for error in errors:
        request.session.flash(error)

def reset_password(form):
    form.new_password.data = None
    form.new_password_confirm.data = None
    return form

class FamiPortOpToolTopView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='top', renderer='top.mako', permission='operator')
    def top(self):
        return HTTPFound(self.request.route_url('search.receipt'))


class FamiPortOpLoginView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='login', renderer='login.mako')
    def get(self):
        return_url = self.request.params.get('return_url', self.request.route_path('top'))

        # loginされてる場合はreturn_urlに移動する
        if self.request.authenticated_userid:
            return HTTPFound(return_url)

        return dict(form=LoginForm(), return_url=return_url)

    @view_config(route_name='login', request_method='POST', renderer='login.mako')
    def post(self):
        return_url = self.request.params.get('return_url')
        form = LoginForm(formdata=self.request.POST)
        if not form.validate():
            flash_error_message(self.request, form.errors.values())
            form.password.data = None
            return dict(form=form, return_url=return_url)

        user = lookup_user_by_credentials(
            self.request,
            form.user_name.data,
            form.password.data
            )

        if not user:
            self.request.session.flash(u'ユーザ名とパスワードの組み合わせが誤っています。')
            form.password.data = None
            return dict(form=form, return_url=return_url)

        if user.is_deactivated:
            self.request.session.flash(u'当アカウントは現在停止されております。')
            self.request.session.flash(u'ご利用したい場合はログインフォーム下のリマインダーリンクで復活してください。')
            form.password.data = None
            return dict(form=form, return_url=return_url)
        elif user.is_first or user.is_expired:
            # パスワードの変更が必要なアカウントの場合はログインさせないで、パスワード変更のtokenを付ける
            aes = AESEncryptor()
            reminder_token = aes.get_token(user.id)
            if user.is_first:
                self.request.session.flash(u'初めてのログインのため、パスワードの変更をお願いいたします。')
            elif user.is_expired:
                self.request.session.flash(u'パスワードの有効期限が切れております。新パスワードへ変更して下さい。')
            return HTTPFound(location=self.request.route_path('change_password', _query=dict(reminder_token=reminder_token)))
        else :
            remember(self.request, user.id)
            return HTTPFound(return_url)


class FamiPortOpLogoutView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='logout', renderer='logout.mako')
    def get(self):
        forget(self.request)
        return HTTPFound(self.request.route_path('login'))

class FamiPortChangePassWord(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='change_password', renderer='change_password.mako', request_method='GET')
    def get(self):
        action_url = self.request.current_route_path()
        form = ChangePassWordForm(csrf_context=self.request.session)
        # 認証した情報からユーザIDを取得
        user_id = self.request.authenticated_userid
        if not user_id:
            reminder_token = self.request.GET.get('reminder_token', None)
            if reminder_token:
                user_id = AESEncryptor.get_id_from_token(reminder_token)

        # 以上二つ方法しかで取得したユーザIDを認めない。
        if not user_id:
            if not self.request.GET:
                self.request.session.flash(u'パスワードの変更はログインまたはパスワードリマインダーでアクセスしてください。')
            else:
                self.request.session.flash(u'予期せぬエラーが発生しました。システム管理者へご連絡下さい。')
            logger.error(
                u'not correct format of the token or accessing without login. user_id:{0}, authenticated_id:{1}, GET:{2}' \
                .format(user_id,
                        self.request.authenticated_userid,
                        self.request.GET))

            return HTTPFound(self.request.route_path('login'))
        return dict(action_url=action_url, form=form)

    @view_config(route_name='change_password', renderer='change_password.mako', request_method='POST')
    def post(self):
        action_url = self.request.current_route_path()
        form = ChangePassWordForm(formdata=self.request.POST, csrf_context=self.request.session)
        user_id = self.request.authenticated_userid
        if not user_id:
            reminder_token = self.request.GET.get('reminder_token', None)
            if reminder_token:
                user_id = AESEncryptor.get_id_from_token(reminder_token)

        if form.validate():
            session = get_db_session(self.request, 'famiport')

            try:
                user = session.query(FamiPortOperator).filter(FamiPortOperator.id == user_id).one()

                if not user.is_matched_password(form.old_password.data):
                    self.request.session.flash(u'旧パスワードは間違います。')
                else:
                    new_encrypted_password = encrypt_password(form.new_password.data)
                    user.password = new_encrypted_password

                    if not user.active:
                        user.active = True
                    session.commit()
                    self.request.session.flash(u'パスワードを変更しました。')
                    return HTTPFound(self.request.route_path('top'))

            except NoResultFound:
                # パスワード変更のpostについて、userを取れない場合はないのため、userが取られない場合は「予期せぬエラー」を出す。
                self.request.session.flash(u'予期せぬエラーが発生しました。システム管理者へご連絡下さい。')
                logger.error(u'not correct format of the token or accessing without login. user_id:{0}, authenticated_id:{1}, GET:{2}' \
                             .format(user_id,
                                     self.request.authenticated_userid,
                                     self.request.GET))
                return HTTPFound(self.request.route_path('login'))

        form = reset_password(form)
        errors_set = form.errors.values()
        for errors in errors_set:
            flash_error_message(self.request, errors)

        return dict(action_url=action_url, form=form)

class FamiPortPasswordReminder(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _get_reminder_url(self, token):
        base_url = self.request.route_url('change_password_reminder')
        params = u'reminder_token={}'.format(token)
        return u'?'.join([base_url, params])

    def _get_html(self, token):
        reminder_url = self._get_reminder_url(token)
        render_param = dict(reminder_url=reminder_url)
        html = render_to_response('altair.app.ticketing:famiport/optool/templates/_password_reminder_mail_content.mako', render_param,request=self.request)
        return html

    @view_config(route_name='password_reminder', renderer='password_reminder.mako', request_method='GET')
    def password_reminder_get(self):
        return dict(form=PasswordReminderForm())

    @view_config(route_name='password_reminder', renderer='password_reminder.mako', request_method='POST')
    def password_reminder_post(self):
        form = PasswordReminderForm(self.request.POST)
        if form.validate():
            user = lookup_user_by_username(request=self.request, user_name=form.user_name.data)

            if user:
                aes = AESEncryptor()
                token = aes.get_token(user.id)
                html = self._get_html(token)
                settings = self.request.registry.settings
                recipient = user.email
                subject = u'FamiPort OPTOOLのアカウント復活について'

                try:
                    sendmail(settings, recipient, subject, html)
                    self.request.session.flash(u'パスワードの更新かアカウントの復活についてのご連絡はご登録いただいたEmailアドレスに送りました。ご確認ください。')
                    return HTTPFound(self.request.route_path('login'))
                except Exception, e:
                    logger.error(
                        "password reminder failed. user_id = {}, error: {}({})".format(user.id, type(e), e.message))
                    self.request.session.flash(u'メールの送信が失敗しました。システム管理者へご連絡下さい。')
            else:
                self.request.session.flash(u'アカウントが見つかりませんでした。入力値をご確認ください。')

        errors_set = form.errors.values()
        for errors in errors_set:
            flash_error_message(self.request, errors)
        return dict(form=form)

    @view_config(route_name='change_password_reminder', renderer='change_password_reminder.mako', request_method='GET')
    def change_password_reminder_get(self):
        reminder_token = self.request.GET.get('reminder_token', None)
        if reminder_token is None:
            self.request.session.flash(u'パスワード再発行用のURLが不正です。パスワードリマインダーで発行して下さい。')
            return HTTPFound(self.request.route_path('login'))

        action_url = self.request.current_route_path(reminder_token=reminder_token)
        form = ReminderChangePassWordForm(csrf_context=self.request.session)

        # パスワードリマインダーのURLでアクセスする場合は強制にログアウトする
        forget(self.request)
        # TokenでユーザIDを取得
        user_id = AESEncryptor.get_id_from_token(reminder_token)

        # 以上二つ方法しかで取得したユーザIDを認めない。
        if not user_id:
            self.request.session.flash(u'パスワード再発行用のURLの有効期限が切れています。パスワードリマインダーで再発行して下さい。')
            return HTTPFound(self.request.route_path('login'))

        return dict(form=form, action_url=action_url)

    @view_config(route_name='change_password_reminder', renderer='change_password_reminder.mako', request_method='POST')
    def change_password_reminder_post(self):
        reminder_token = self.request.params.get('reminder_token', None)
        if reminder_token is None:
            self.request.session.flash(u'パスワード再発行用のURLが不正です。パスワードリマインダーで発行して下さい。')
            return HTTPFound(self.request.route_path('login'))

        action_url = self.request.current_route_path(reminder_token=reminder_token)
        form = ReminderChangePassWordForm(formdata=self.request.POST, csrf_context=self.request.session)

        user_id = AESEncryptor.get_id_from_token(reminder_token)

        if form.validate():
            session = get_db_session(self.request, 'famiport')

            try:
                user = session.query(FamiPortOperator).filter(FamiPortOperator.id == user_id).one()

                if not user.is_valid_email(form.email.data):
                    self.request.session.flash(u'Eメールアドレスが不正です。')
                else:
                    new_encrypted_password = encrypt_password(form.new_password.data)
                    user.password = new_encrypted_password

                    if not user.active:
                        user.active = True
                    session.commit()
                    self.request.session.flash(u'パスワードを再設定しました。')
                    return HTTPFound(self.request.route_path('top'))

            except NoResultFound:
                # パスワード再設定のpostについて、userを取れない場合はないのため、userが取られない場合は「予期せぬエラー」を出す。
                self.request.session.flash(u'予期せぬエラーが発生しました。システム管理者へご連絡下さい。')
                logger.error(
                    u'not correct format of the token or accessing without login. user_id:{0}, authenticated_id:{1}, reminder_token:{2}, GET:{3}' \
                    .format(user_id,
                            self.request.authenticated_userid,
                            reminder_token,
                            self.request.GET))
                return HTTPFound(self.request.route_path('login'))

        form = reset_password(form)
        errors_set = form.errors.values()
        for errors in errors_set:
            flash_error_message(self.request, errors)

        return dict(form=form, action_url=action_url)

class FamiPortOpToolExampleView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='example.page_needs_authentication', renderer='example/page_needs_authentication.mako', permission='operator')
    def page_needs_authentication(self):
        return dict()

class FamiPortSearchView(object):
    SEARCH_LIMIT_COUNT = 100000

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = get_db_session(self.request, 'famiport')

    def _flash_search_limit_count_message(self):
        self.request.session.flash(u'対象が多いため、検索条件を絞ってください')

    # @view_config(route_name='index', renderer='altair.app.ticketing.famiport.optool:templates/order_search.html', permission='operator')
    @view_config(route_name='search.receipt', renderer='altair.app.ticketing.famiport.optool:templates/receipt_search.mako', permission='operator')
    def search_receipt(self):
        form = SearchReceiptForm(self.request.params)
        if not self.request.GET:
            return dict(form=form)
        if not form.validate():
            errors = u'・'.join(sum(form.errors.values(), []))
            self.request.session.flash(errors)
            return dict(form=form)
        page = int(self.request.GET.get('page', 1))
        session = get_db_session(self.request, 'famiport')
        query = lookup_receipt_by_searchform_data(self.request, session, self.request.GET)

        if query.count() >= self.SEARCH_LIMIT_COUNT:
            self._flash_search_limit_count_message()
            return dict(form=form)

        receipts = get_paginator(self.request, query, page)
        return dict(form=form, receipts=receipts, vh=ViewHelpers(self.request))

    @view_config(route_name='search.performance', permission='operator',
                 renderer='altair.app.ticketing.famiport.optool:templates/performance_search.mako')
    def search_performance(self):
        form = SearchPerformanceForm(self.request.params)
        if not self.request.GET:
            return dict(form=form)
        if not form.validate():
            errors = u'・'.join(sum(form.errors.values(), []))
            self.request.session.flash(errors)
            return dict(form=form)
        page = int(self.request.GET.get('page', 1))
        query = lookup_performance_by_searchform_data(self.request, self.request.GET)

        if query.count() >= self.SEARCH_LIMIT_COUNT:
            self._flash_search_limit_count_message()
            return dict(form=form)

        performances = get_paginator(self.request, query, page)
        return dict(form=form, performances=performances, vh=ViewHelpers(self.request))

    @view_config(route_name='search.refund_performance', permission='operator',
                 renderer='altair.app.ticketing.famiport.optool:templates/refund_performance_search.mako')
    def search_refund_performance(self):
        form = SearchRefundPerformanceForm(self.request.params)
        if not self.request.GET:
            return dict(form=form)
        if not form.validate():
            errors = u'・'.join(sum(form.errors.values(), []))
            self.request.session.flash(errors)
            return dict(form=form)
        page = int(self.request.GET.get('page', 1))
        query = lookup_refund_performance_by_searchform_data(self.request, self.request.GET)

        if query.count() >= self.SEARCH_LIMIT_COUNT:
            self._flash_search_limit_count_message()
            return dict(form=form)

        refund_performances = get_paginator(self.request, query, page)
        return dict(form=form, refund_performances=refund_performances, vh=ViewHelpers(self.request))

    @view_config(route_name='search.refund_ticket', request_method='GET', permission='operator',
                 renderer='altair.app.ticketing.famiport.optool:templates/refund_ticket_search.mako')
    def search_refund_ticket(self):
        form = RefundTicketSearchForm(self.request.params)
        if not self.request.GET:
            return dict(form=form)
        if not form.validate():
            errors = u'・'.join(sum(form.errors.values(), []))
            self.request.session.flash(errors)
            return dict(form=form)
        page = int(self.request.GET.get('page', 1))
        query = search_refund_ticket_by(self.request, self.request.GET)

        if query.count() >= self.SEARCH_LIMIT_COUNT:
            self._flash_search_limit_count_message()
            return dict(form=form)

        entries = get_paginator(self.request, query, page)
        rts_helper = RefundTicketSearchHelper(self.request)
        columns = rts_helper.get_columns()
        return dict(form=form, entries=entries, rts_helper=rts_helper, columns=columns)

# TODO Make sure the permission of each operation
class FamiPortDetailView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


    @view_config(route_name='receipt.detail', renderer='altair.app.ticketing.famiport.optool:templates/receipt_detail.mako')
    def show_order_detail(self):
        receipt = self.context.receipt
        return dict(receipt=receipt, vh=ViewHelpers(self.request),)

    @view_config(route_name='performance.detail', renderer='altair.app.ticketing.famiport.optool:templates/performance_detail.mako', permission='operator')
    def show_performance_detail(self):
        performance = self.context.performance
        return dict(performance=performance, vh=ViewHelpers(self.request),)

    @view_config(route_name='refund_performance.detail', renderer='altair.app.ticketing.famiport.optool:templates/refund_performance_detail.mako')
    def show_refund_performance_detail(self):
        performance = self.context.performance
        refund_entry = self.context.refund_entry
        return dict(performance=performance, refund_entry=refund_entry, vh=ViewHelpers(self.request))

# TODO Make sure the permission of each operation
class FamiPortRebookOrderView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='rebook_order', request_method='GET', renderer='altair.app.ticketing.famiport.optool:templates/rebook_order.mako', permission='operator')
    def rebook_order(self):
        form = RebookOrderForm()
        receipt = self.context.receipt
        form.cancel_reason_code.data = receipt.cancel_reason_code
        form.cancel_reason_text.data = receipt.cancel_reason_text
        return dict(form=form, receipt=receipt, now=datetime.now(), vh=ViewHelpers(self.request))

    @view_config(xhr=True, route_name='rebook_order', request_method='POST', match_param='action=rebook', renderer='json', permission='operator')
    def post_rebook_order(self):
        session = get_db_session(self.request, name="famiport")
        now = datetime.now()
        receipt = self.context.receipt
        order = receipt.famiport_order
        old_management_number = receipt.reserve_number
        new_management_number = u''
        error = u''
        form = RebookOrderForm(self.request.POST)
        if form.validate():
            cancel_code = self.request.POST.get('cancel_reason_code')
            cancel_text = self.request.POST.get('cancel_reason_text')

            errors = validate_rebook_cond(receipt, now)
            if not errors:
                try:
                    new_receipt = order.recreate_receipt(now,
                                                         self.request,
                                                         receipt,
                                                         reason=None,
                                                         cancel_reason_code=cancel_code,
                                                         cancel_reason_text=cancel_text)
                except Exception as e:
                    return dict(old_identifier=old_management_number,
                                new_identifier=new_management_number,
                                error=unicode(e))

                if new_receipt:
                    new_management_number = new_receipt.reserve_number
                else:
                    if receipt.type == FamiPortReceiptType.Payment.value:
                        error = u'未入金の支払込票は同席番再予約しませんので、予約番号（{}）は変更されていません。'.format(receipt.reserve_number)
                    elif receipt.type == FamiPortReceiptType.Ticketing.value:
                        error = u'未発券の引換票は同席番再予約しませんので、予約番号（{}）は変更されていません。'.format(receipt.reserve_number)
                    else:
                        error = u'未入金/未発券の引換票は同席番再予約しませんので、予約番号（{}）は変更されていません。'.format(receipt.reserve_number)
            else:
                error = u'<br>・'.join(errors)

        else:
            error = u'<br>・'.join(sum(form.errors.values(), []))

        session.commit()
        return dict(old_identifier=old_management_number,
                    new_identifier=new_management_number,
                    error=error)

    @view_config(route_name='rebook_order', request_method='POST', match_param='action=fix-reason', renderer='altair.app.ticketing.famiport.optool:templates/rebook_order.mako', permission='operator')
    def post_fix_reason(self):
        form = RebookOrderForm(self.request.POST)
        if form.validate():
            self.context.update_cancel_reason(self.request.POST)
            self.request.session.flash(u'理由コードと理由テキストを更新しました')
        else:
            error = u'・'.join(sum(form.errors.values(), []))
            self.request.session.flash(error)

        return HTTPFound(self.request.route_url('rebook_order', action='show', receipt_id=self.context.receipt.id))

    @view_config(xhr=True, route_name='rebook_order', request_method='POST', match_param='action=reprint', renderer='json', permission='operator')
    def reprint_ticket(self):
        session = get_db_session(self.request, name="famiport")
        receipt = self.context.receipt
        order = receipt.famiport_order
        client_code = order.client_code
        error = u''
        form = RebookOrderForm(self.request.POST)
        if form.validate():
            cancel_code = self.request.POST.get('cancel_reason_code')
            cancel_text = self.request.POST.get('cancel_reason_text')

            errors = validate_reprint_cond(receipt, datetime.now())

            if not errors:
                mark_order_reissueable_by_order_no(request=self.request,
                                                   session=session,
                                                   client_code=client_code,
                                                   order_no=order.order_no,
                                                   cancel_reason_code=cancel_code,
                                                   cancel_reason_text=cancel_text)

            else:
                error = u'・'.join(errors)
        else:
            error = u'・'.join(sum(form.errors.values(), []))

        session.commit()
        return dict(error=error,)

class FamiPortDownloadRefundTicketView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='download.refund_ticket', renderer='csv', permission='operator')
    def download_csv(self):
        refund_entries = search_refund_ticket_by(self.request, self.request.GET)
        rts_helper = RefundTicketSearchHelper(self.request)
        header = [column[1] for column in rts_helper.get_columns()]

        rts_helper = RefundTicketSearchHelper(self.request)
        rows = []
        for entry in refund_entries:
            famiport_refund_entry = entry.FamiPortRefundEntry
            famiport_shop = rts_helper.get_famiport_shop_by_code(famiport_refund_entry.shop_code)
            event_code_1 = famiport_refund_entry.famiport_ticket.famiport_order.famiport_performance.famiport_event.code_1
            event_code_2 = famiport_refund_entry.famiport_ticket.famiport_order.famiport_performance.famiport_event.code_2
            ticketing_shop_code = famiport_refund_entry.famiport_ticket.famiport_order.ticketing_famiport_receipt.shop_code
            rows.append([
                unicode(rts_helper.get_refund_status_text(famiport_refund_entry.refunded_at)),
                unicode(famiport_shop.district_code if famiport_shop else u''),
                unicode(famiport_shop.branch_code if famiport_shop else u''),
                unicode(ticketing_shop_code),
                unicode(rts_helper.get_shop_name_text(rts_helper.get_famiport_shop_by_code(ticketing_shop_code))),
                unicode(rts_helper.get_management_number_from_famiport_order_identifier(famiport_refund_entry.famiport_ticket.famiport_order.famiport_order_identifier)),
                unicode(famiport_refund_entry.famiport_ticket.barcode_number),
                unicode(event_code_1),
                unicode(event_code_2),
                unicode(rts_helper.format_date(famiport_refund_entry.famiport_ticket.famiport_order.performance_start_at)),
                unicode(famiport_refund_entry.famiport_ticket.famiport_order.famiport_performance.famiport_event.name_1),
                unicode(famiport_refund_entry.total_amount),
                unicode(rts_helper.format_datetime(famiport_refund_entry.refunded_at)),
                unicode(famiport_refund_entry.shop_code),
                unicode(rts_helper.get_shop_name_text(famiport_shop)),
                unicode(famiport_refund_entry.famiport_ticket.famiport_order.order_no),
                unicode(famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment.name if famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment else u'-'),
                unicode(famiport_refund_entry.famiport_ticket.famiport_order.customer_name),
            ])

        return {'header':header, 'rows': rows}


class APIError(Exception):
    pass


class APIBadParameterError(APIError):
    pass

class APINotFoundError(APIError):
    pass


@view_defaults(permission='authenticated')
class FamiPortAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @reify
    def session(self):
        return get_db_session(self.request, 'famiport')

    def preview_pictures(self, **kwargs):
        return get_ticket_preview_pictures(self.request, **kwargs)

    def _render_ticket_common(self):
        try:
            famiport_receipt_id = self.request.matchdict['receipt_id']
        except KeyError:
            raise APIBadParameterError('missing receipt_id')
        try:
            famiport_receipt = self.session.query(FamiPortReceipt).filter(FamiPortReceipt.id == famiport_receipt_id, FamiPortReceipt.canceled_at.is_(None)).one()
        except NoResultFound:
            raise APINotFoundError()
        # 前払のみの場合はチケットがないのでプレビュー不要
        if famiport_receipt.famiport_order.type == FamiPortOrderType.PaymentOnly.value:
            images = []
        else:
            famiport_client = famiport_receipt.famiport_order.famiport_client
            famiport_tickets = famiport_receipt.famiport_order.famiport_tickets
            images = self.preview_pictures(
                discrimination_code=unicode(famiport_client.playguide.discrimination_code_2),
                client_code=famiport_client.code,
                order_id=famiport_receipt.famiport_order_identifier,
                barcode_no=famiport_receipt.barcode_no or u'0000000000000',
                name=famiport_receipt.famiport_order.customer_name or u'',
                member_id=u'',
                address_1=famiport_receipt.famiport_order.customer_address_1 or u'',
                address_2=famiport_receipt.famiport_order.customer_address_2 or u'',
                identify_no=u'',
                response_image_type='pdf',
                tickets=[
                    dict(
                        barcode_no=famiport_ticket.barcode_number,
                        template_code=famiport_ticket.template_code,
                        data=famiport_ticket.data
                        )
                    for famiport_ticket in famiport_tickets
                    ]
                )
        return images, famiport_receipt

    @view_config(route_name='receipt.ticket.info')
    def render_ticket_info(self):
        try:
            images, famiport_receipt = self._render_ticket_common()
        except APINotFoundError:
            return Response(
                content_type='application/json',
                charset='utf-8',
                status=404,
                body=json.dumps(
                    {
                        'status': 'error',
                        'message': 'not found'
                        },
                    ensure_ascii=False,
                    encoding='utf-8'
                    )
                )
        except APIBadParameterError:
            return Response(
                content_type='application/json',
                charset='utf-8',
                status=400,
                body=json.dumps(
                    {
                        'status': 'error',
                        'message': 'bad request'
                        },
                    ensure_ascii=False,
                    encoding='utf-8'
                    )
                )
        except FamiEncodeError as e:
            return Response(
                content_type='application/json',
                charset='utf-8',
                status=500,
                body=json.dumps(
                    {
                        'status': 'invalid_encode',
                        'message': e.message
                        },
                    ensure_ascii=False,
                    encoding='utf-8'
                    )
                )
        except Exception as e:
            logger.exception('error')
            return Response(
                content_type='application/json',
                charset='utf-8',
                status=500,
                body=json.dumps(
                    {
                        'status': 'error',
                        'message': e.message
                        },
                    ensure_ascii=False,
                    encoding='utf-8'
                    )
                )
        return Response(
            content_type='application/json',
            charset='utf-8',
            status=200,
            body=json.dumps(
                {
                    'status': 'ok',
                    'pages': [
                        self.request.route_path('receipt.ticket.render', receipt_id=famiport_receipt.id, page=page)
                        for page in range(0, len(images))
                        ]
                    },
                ensure_ascii=False,
                encoding='utf-8'
                )
            )

    @view_config(route_name='receipt.ticket.render')
    def render_ticket_render(self):
        try:
            try:
                page = self.request.matchdict['page']
                page = int(page)
            except (TypeError, ValueError, KeyError):
                raise APIBadParameterError('missingmissing  page')
            images, famiport_receipt = self._render_ticket_common()
            if page < 0 or page >= len(images):
                raise APIBadParameterError('page')
        except APINotFoundError:
            return Response(
                content_type='application/json',
                charset='utf-8',
                status=404,
                body=json.dumps(
                    {
                        'status': 'error',
                        'message': 'not found'
                        },
                    ensure_ascii=False,
                    encoding='utf-8'
                    )
                )
        except APIBadParameterError as e:
            return Response(
                content_type='application/json',
                charset='utf-8',
                status=400,
                body=json.dumps(
                    {
                        'status': 'error',
                        'message': e.message
                        },
                    ensure_ascii=False,
                    encoding='utf-8'
                    )
                )
        except Exception as e:
            logger.exception('error')
            return Response(
                content_type='application/json',
                charset='utf-8',
                status=500,
                body=json.dumps(
                    {
                        'status': 'error',
                        'message': e.message
                        },
                    ensure_ascii=False,
                    encoding='utf-8'
                    )
                )
        return Response(
            content_type='application/pdf',
            status=200,
            body=images[page]
            )
