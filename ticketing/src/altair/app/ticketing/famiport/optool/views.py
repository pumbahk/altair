# encoding: utf-8

import logging
import json
from datetime import datetime
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.response import Response
from pyramid.decorator import reify
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
    search_refund_ticket_by
)
from .forms import (
    LoginForm,
    SearchPerformanceForm,
    SearchReceiptForm,
    RebookOrderForm,
    SearchRefundPerformanceForm,
    RefundTicketSearchForm
)
from .utils import ValidateUtils
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
        user = lookup_user_by_credentials(
            self.request,
            form.user_name.data,
            form.password.data
            )
        if user is None:
            self.request.session.flash(u'ユーザ名とパスワードの組み合わせが誤っています')
            return dict(form=form, return_url=return_url)

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
        paginator = get_paginator(self.request, lookup_receipt_by_searchform_data(self.request, self.request.GET), page)
        return dict(form=form, paginator=paginator, vh=ViewHelpers(self.request))

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
        paginator = get_paginator(self.request, lookup_performance_by_searchform_data(self.request, self.request.GET), page)
        return dict(form=form, paginator=paginator, vh=ViewHelpers(self.request))

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
        paginator = get_paginator(self.request, lookup_refund_performance_by_searchform_data(self.request, self.request.GET), page)
        return dict(form=form, paginator=paginator, vh=ViewHelpers(self.request))

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
        paginator = get_paginator(self.request, search_refund_ticket_by(self.request, self.request.GET), page)
        rts_helper = RefundTicketSearchHelper(self.request)
        columns = rts_helper.get_columns()
        return dict(form=form, paginator=paginator, rts_helper=rts_helper, columns=columns)

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
        old_management_number = vh.get_management_number_from_famiport_order_identifier(receipt.famiport_order_identifier)
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

                new_management_number = vh.get_management_number_from_famiport_order_identifier(new_receipt.famiport_order_identifier)
            else:
                error = u'・'.join(ValidateUtils.validate_rebook_cond(receipt, datetime.now()))

        else:
            error = u'・'.join(sum(form.errors.values(), []))

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
        refund_entries = search_refund_ticket_by(self.request, self.request.POST)
        rts_helper = RefundTicketSearchHelper(self.request)
        header = [column[1] for column in rts_helper.get_columns()]

        rts_helper = RefundTicketSearchHelper(self.request)
        rows = []
        for entry in refund_entries:
            famiport_refund_entry = entry.FamiPortRefundEntry
            famiport_shop = rts_helper.get_famiport_shop_by_code(famiport_refund_entry.shop_code)
            event_code_1 = famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment.famiport_performance.famiport_event.code_1
            event_code_2 = famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment.famiport_performance.famiport_event.code_2
            ticketing_shop_code = famiport_refund_entry.famiport_ticket.famiport_order.ticketing_famiport_receipt.shop_code
            rows.append([
                unicode(rts_helper.get_refund_status_text(famiport_refund_entry.refunded_at)),
                unicode(famiport_shop.district_code if famiport_shop else u''),
                unicode(famiport_shop.branch_code if famiport_shop else u''),
                unicode(ticketing_shop_code),
                unicode(rts_helper.get_shop_name_text(rts_helper.get_famiport_shop_by_code(ticketing_shop_code))),
                unicode(rts_helper.get_management_number_from_famiport_order_identifier(famiport_refund_entry.famiport_ticket.famiport_order.famiport_order_identifier)),
                unicode(famiport_refund_entry.famiport_ticket.barcode_number),
                unicode(u'-'.join([event_code_1,event_code_2])),
                unicode(rts_helper.format_date(famiport_refund_entry.famiport_ticket.famiport_order.performance_start_at)),
                unicode(famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment.famiport_performance.famiport_event.name_1),
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
