# encoding: utf-8

import logging
import json
from datetime import datetime, timedelta
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.response import Response
from pyramid.decorator import reify
from webob.multidict import MultiDict
from webhelpers import paginate
from sqlalchemy.orm.exc import NoResultFound
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
    AccountReminderForm
)
from .utils import ValidateUtils, AESEncryptor
from .helpers import (
    ViewHelpers,
    get_paginator,
    RefundTicketSearchHelper,
)

logger = logging.getLogger(__name__)

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

    def _can_login(self, operator):
        status = True
        errors = []
        if operator is None:
            errors.append(u'ユーザ名とパスワードの組み合わせが誤っています。')
            status = False
        elif operator.expired_at and datetime.now() - operator.expired_at > timedelta(days=30):
            errors.append(u'このアカウントの使用期限は切ったため、ご利用されることはできません。')
            errors.append(u'ご利用したい場合はログインフォーム下のリマインダーリンクで復旧してください。')
            status = False

        if errors:
            for msg in errors:
                self.request.session.flash(msg)
        return status

    def _need_change_password(self, operator):
        status = False
        warnings = []

        if not operator.active:
            status = True
            warnings.append(u'初めてログインしたため、パスワードをご変更ください。')
        elif operator.expired_at and datetime.now() > operator.expired_at:
            status = True
            warnings.append(u'パスワードの有効期限が切りましたため、パスワードをご変更ください。')

        if warnings:
            for msg in warnings:
                self.request.session.flash(msg)
        return status

    @view_config(route_name='login', renderer='login.mako')
    def get(self):
        return_url = self.request.params.get('return_url', '')
        return dict(form=LoginForm(), return_url=return_url)
        
    @view_config(route_name='login', request_method='POST', renderer='login.mako')
    def post(self):
        return_url = self.request.params.get('return_url')
        if not return_url:
            return_url = self.request.route_path('top')
        form = LoginForm(formdata=self.request.POST)
        if not form.validate():
            return dict(form=form, return_url=return_url)
        operator = lookup_user_by_credentials(
            self.request,
            form.user_name.data,
            form.password.data
            )
        if not self._can_login(operator):
            return dict(form=form, return_url=return_url)
        else:
            remember(self.request, operator.id)
        if self._need_change_password(operator):
            return HTTPFound(location=self.request.route_url('change_password'))

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

    def _can_change_password(self, form, operator):
        status = True
        errors = []

        if operator:
            encrypted_password = encrypt_password(form.password.data, operator.password)
            if not encrypted_password == operator.password:
                status = False
                errors.append(u'ご利用しているパスワードは間違っているため、ご確認ください。')
        else:
            status = False
            errors.append(u'パスワードを変更するユーザのアカウントは見つからないため、ご確認ください。')
        if errors:
            for msg in errors:
                self.request.session.flash(msg)
        return status

    @view_config(route_name='change_password', renderer='change_password.mako', request_method='GET')
    def change_password_get(self):
        # 認証した情報からユーザIDを取得
        id_by_authenticated = self.request.authenticated_userid
        # TokenのバリーデトでユーザIDを取得
        token = self.request.GET.get('token')
        id_by_token = AESEncryptor.verify_token(token) if token else None
        user_id = id_by_token or id_by_authenticated

        # 以上二つ方法しかユーザIDを取得する方法がない。
        if not user_id:
            self.request.session.flash(u'パスワードを変更するユーザのアカウントは見つからないため、ご確認ください。')
            return HTTPFound(self.request.route_path('login'))
        else:
            return dict(form=ChangePassWordForm(formdata=MultiDict(user_id=user_id)))

    @view_config(route_name='change_password', renderer='change_password.mako', request_method='POST')
    def change_password_post(self):
        form = ChangePassWordForm(formdata=self.request.POST)
        if form.validate():
            operator, session = lookup_user_by_id(request=self.request, id=form.user_id.data, return_session=True)
            if self._can_change_password(form, operator):
                new_encrypted_password = encrypt_password(form.new_password.data)
                operator.password = new_encrypted_password

                if not operator.active:
                    operator.active = True

                session.commit()
                session.close()
                self.request.session.flash(u'パスワードを変更しました。')
                return HTTPFound(self.request.route_url('top'))

        return dict(form=form)

class AccountReminder(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _create_reminder_url(self, token):
        base_url = self.request.route_url('change_password')
        params = u'token={}'.format(token)
        return u'?'.join([base_url, params])

    def _is_valid_account(self, form, operator):
        status = True
        errors = []

        if operator:
            if not (operator.email and operator.email == form.email.data):
                status = False
                errors.append(u'ご提供したEMAILアドレスは登録されていないので、EMAILアドレスをご確認してください。')
        else:
            errors.append(u'パスワードを変更するユーザのアカウントは見つからないため、管理者にお問い合わせください。')

        if errors:
            for msg in errors:
                self.request.session.flash(msg)
        return status

    @view_config(route_name='account_reminder', renderer='account_reminder.mako')
    def account_reminder(self):
        if self.request.method == 'POST':
            form = AccountReminderForm(self.request.POST)
            if form.validate():
                operator = lookup_user_by_username(self.request, form.user_name.data)
                if self._is_valid_account(form, operator):
                    aes = AESEncryptor()
                    token = aes.get_token(operator.id)
                    reminder_url = self._create_reminder_url(token)
                    return dict(form=AccountReminderForm(),reminder_url=reminder_url)

                return dict(form=form)
        return dict(form=AccountReminderForm())


class FamiPortOpToolExampleView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='example.page_needs_authentication', renderer='example/page_needs_authentication.mako', permission='operator')
    def page_needs_authentication(self):
        return dict()

class FamiPortSearchView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = get_db_session(self.request, 'famiport')

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
        receipt = self.context.receipt
        order = receipt.famiport_order
        client_code = order.client_code
        vh=ViewHelpers(self.request)
        old_management_number = receipt.reserve_number
        new_management_number = u''
        error = u''
        form = RebookOrderForm(self.request.POST)
        if form.validate():
            cancel_code = self.request.POST.get('cancel_reason_code')
            cancel_text = self.request.POST.get('cancel_reason_text')

            if not ValidateUtils.validate_rebook_cond(receipt, datetime.now()):
                make_suborder_by_order_no(request=self.request,
                                          session=session,
                                          client_code=client_code,
                                          order_no=order.order_no,
                                          cancel_reason_code=cancel_code,
                                          cancel_reason_text=cancel_text)

                if receipt.type == FamiPortReceiptType.Payment.value:
                    new_receipt = filter(lambda x: x.canceled_at is None and x.type == FamiPortReceiptType.Payment.value, order.famiport_receipts).pop()
                elif receipt.type == FamiPortReceiptType.Ticketing.value:
                    new_receipt = filter(lambda x: x.canceled_at is None and x.type == FamiPortReceiptType.Ticketing.value, order.famiport_receipts).pop()
                else:
                    new_receipt = filter(lambda x: x.canceled_at is None and x.type == FamiPortReceiptType.CashOnDelivery.value, order.famiport_receipts).pop()

                new_management_number = new_receipt.reserve_number
            else:
                error = u'<br>・'.join(ValidateUtils.validate_rebook_cond(receipt, datetime.now()))

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

            if not ValidateUtils.validate_reprint_cond(receipt, datetime.now()):
                mark_order_reissueable_by_order_no(request=self.request,
                                                   session=session,
                                                   client_code=client_code,
                                                   order_no=order.order_no,
                                                   cancel_reason_code=cancel_code,
                                                   cancel_reason_text=cancel_text)

            else:
                error = u'・'.join(ValidateUtils.validate_reprint_cond(receipt, datetime.now()))
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
                unicode(famiport_refund_entry.ticket_payment),
                unicode(rts_helper.format_datetime(famiport_refund_entry.refunded_at)),
                unicode(famiport_refund_entry.shop_code),
                unicode(rts_helper.get_shop_name_text(famiport_shop)),
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
