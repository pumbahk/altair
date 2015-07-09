# encoding: utf-8

import logging
from datetime import datetime
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from altair.sqlahelper import get_db_session
from altair.app.ticketing.famiport.models import (
    FamiPortPerformance,
    FamiPortEvent,
    FamiPortOrder,
    FamiPortOrderType,
    FamiPortRefundEntry
)
from .api import (
    lookup_user_by_credentials,
    lookup_performance_by_searchform_data,
    lookup_refund_performance_by_searchform_data,
    lookup_receipt_by_searchform_data,
    search_refund_ticket_by
)
from ..internal_api import make_suborder_by_order_no, mark_order_reissueable_by_order_no
from .forms import (
    LoginForm,
    SearchPerformanceForm,
    SearchReceiptForm,
    RebookOrderForm,
    SearchRefundPerformanceForm,
    RefundTicketSearchForm
)
from webhelpers import paginate
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from .helpers import (
    ViewHelpers,
    get_paginator,
    RefundTicketSearchHelper,
)
from ..exc import FamiPortAPIError

logger = logging.getLogger(__name__)

class FamiPortOpToolTopView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='top', renderer='top.mako', permission='operator')
    def top(self):
        return dict()


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
        form = SearchReceiptForm()

        if self.request.params:
            postdata = self.request.params
            form = SearchReceiptForm(postdata)
            if form.validate():
                receipts = lookup_receipt_by_searchform_data(self.request, postdata)
                count = len(receipts)
                if count == 0:
                    self.request.session.flash(u'該当するデータはありませんでした')
                page_url = PageURL_WebOb_Ex(self.request)
                pages = paginate.Page(receipts,
                                      page=self.request.GET.get('page', '1'),
                                      item_count=count,
                                      items_per_page=20,
                                      url=page_url)
            else:
                for error in form.errors.values():
                    logger.info('validation failed:{}'.format(error))

                errors = u'・'.join(sum(form.errors.values(), []))
                self.request.session.flash(errors)
                count = None
                pages = []
        else:
            count = None
            pages = []

        return dict(form=form,
                    count=count,
                    entries=pages,
                    vh=ViewHelpers(),)

    @view_config(route_name='search.performance', permission='operator',
                 renderer='altair.app.ticketing.famiport.optool:templates/performance_search.mako')
    def search_performance(self):
        form = SearchPerformanceForm()

        if self.request.params:
            postdata = self.request.params
            form = SearchPerformanceForm(postdata)
            if form.validate():
                performances = lookup_performance_by_searchform_data(self.request, postdata)
                count = len(performances)
                page_url = PageURL_WebOb_Ex(self.request)
                pages = paginate.Page(performances,
                                     page=self.request.GET.get('page', '1'),
                                     item_count=count,
                                     items_per_page=20,
                                     url=page_url)
            else:
                for error in form.errors.values():
                    logger.info('validation failed:{}'.format(error))

                errors = u'・'.join(sum(form.errors.values(), []))
                self.request.session.flash(errors)
                if not postdata.get('event_code_1') and postdata.get('event_code_2'):
                    self.request.session.flash(u'mainとsubセットでご入力下さい')
                count = None
                pages = []
        else:
            count = None
            pages = []

        return dict(form=form,
                    count=count,
                    entries=pages)

    @view_config(route_name='search.refund_performance', permission='operator',
                 renderer='altair.app.ticketing.famiport.optool:templates/refund_performance_search.mako')
    def search_refund_performance(self):
        form = SearchRefundPerformanceForm()
        if self.request.params:
            postdata = self.request.params
            form = SearchRefundPerformanceForm(postdata)
            if form.validate():
                results = lookup_refund_performance_by_searchform_data(self.request, postdata)
                count = len(results)
                page_url = PageURL_WebOb_Ex(self.request)
                pages = paginate.Page(results,
                                      page=self.request.GET.get('page', '1'),
                                      item_count=count,
                                      items_per_page=20,
                                      url=page_url)
            else:
                for error in form.errors.values():
                    logger.info('validation failed:{}'.format(error))

                errors = u'・'.join(sum(form.errors.values(), []))
                self.request.session.flash(errors)
                count = None
                pages = []
        else:
            count = None
            pages = []
        return dict(form=form,
                    count=count,
                    entries=pages,
                    vh=ViewHelpers())

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
        return dict(receipt=receipt, vh=ViewHelpers(),)

    @view_config(route_name='performance.detail', renderer='altair.app.ticketing.famiport.optool:templates/performance_detail.mako', permission='operator')
    def show_performance_detail(self):
        performance = self.context.performance
        return dict(performance=performance, h=ViewHelpers(),)

    @view_config(route_name='refund_performance.detail', renderer='altair.app.ticketing.famiport.optool:templates/refund_performance_detail.mako')
    def show_refund_performance_detail(self):
        performance = self.context.performance
        return dict(performance=performance,)

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
        return dict(form=form, receipt=receipt, now=datetime.now())

    @view_config(xhr=True, route_name='rebook_order', request_method='POST', match_param='action=rebook', renderer='json', permission='operator')
    def post_rebook_order(self):
        session = get_db_session(self.request, name="famiport")
        receipt = self.context.receipt
        order = receipt.famiport_order
        old_fami_identifier = receipt.famiport_order_identifier
        cancel_code = self.request.POST.get('cancel_reason_code')
        cancel_text = self.request.POST.get('cancel_reason_text')

        if receipt.is_rebookable(datetime.now()):
            make_suborder_by_order_no(request=self.request,
                                      session=session,
                                      order_no=order.order_no,
                                      cancel_reason_code=cancel_code,
                                      cancel_reason_text=cancel_text)
            if order.type == FamiPortOrderType.PaymentOnly.value:
                new_receipt = order.payment_famiport_receipt
            elif order.type in (FamiPortOrderType.Payment.value, FamiPortOrderType.Ticketing.value, FamiPortOrderType.CashOnDelivery.value):
                # Ordertype.Paymentの時はticketing側のレシートが取得される
                new_receipt = order.ticketing_famiport_receipt
            else:
                raise FamiPortAPIError(u'make_suborder_by_order_no failed')

            new_fami_identifier = new_receipt.famiport_order_identifier
        else:
            raise FamiPortAPIError(u'this receipt is not rebookable!')
        session.commit()

        return dict(old_identifier=old_fami_identifier, new_identifier=new_fami_identifier)

    @view_config(route_name='rebook_order', request_method='POST', match_param='action=fix-reason', renderer='altair.app.ticketing.famiport.optool:templates/rebook_order.mako', permission='operator')
    def post_fix_reason(self):
        self.context.update_cancel_reason(self.request.POST)
        self.request.session.flash(u'理由コードと理由テキストを更新しました')
        return HTTPFound(self.request.route_url('rebook_order', action='show', receipt_id=self.context.receipt.id))

    @view_config(xhr=True, route_name='rebook_order', request_method='POST', match_param='action=reprint', renderer='json', permission='operator')
    def reprint_ticket(self):
        session = get_db_session(self.request, name="famiport")
        receipt = self.context.receipt
        order = receipt.famiport_order
        old_fami_identifier = receipt.famiport_order_identifier
        cancel_code = self.request.POST.get('cancel_reason_code')
        cancel_text = self.request.POST.get('cancel_reason_text')

        if receipt.is_reprintable(datetime.now()):
            mark_order_reissueable_by_order_no(request=self.request,
                                      session=session,
                                      order_no=order.order_no,
                                      cancel_reason_code=cancel_code,
                                      cancel_reason_text=cancel_text)
            new_receipt = order.ticketing_famiport_receipt
            new_fami_identifier = new_receipt.famiport_order_identifier
        else:
            raise FamiPortAPIError(u'this receipt is not reprintable!')
        session.commit()

        return dict(old_identifier=old_fami_identifier, new_identifier=new_fami_identifier)

class FamiPortDownloadRefundTicketView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='download.refund_ticket', renderer='csv', permission='operator')
    def download_csv(self):
        refund_entries = search_refund_ticket_by(self.request, self.request.POST)

        header = [
            u'払戻状況',
            u'地区',
            u'営業所',
            u'発券店番',
            u'発券店舗名',
            u'管理番号',
            u'バーコード',
            u'興行コード-サブコード',
            u'公演日',
            u'興行名',
            u'返金額',
            u'払戻日時',
            u'払戻店番',
            u'払戻店舗名',
        ]

        rts_helper = RefundTicketSearchHelper(self.request)
        rows = []
        for famiport_refund_entry in refund_entries:
            famiport_shop = rts_helper.get_famiport_shop_by_code(famiport_refund_entry.shop_code)
            event_code_1 = famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment.famiport_performance.famiport_event.code_1
            event_code_2 = famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment.famiport_performance.famiport_event.code_2
            rows.append([
                unicode(rts_helper.get_refund_status_text(famiport_refund_entry.refunded_at)),
                unicode(famiport_shop.district_code if famiport_shop else u''),
                unicode(famiport_shop.branch_code if famiport_shop else u''),
                unicode(famiport_refund_entry.famiport_ticket.famiport_order.issuing_shop_code),
                unicode(famiport_refund_entry.famiport_ticket.famiport_order.ticketing_famiport_receipt.get_shop_name(self.request)),
                unicode(rts_helper.get_management_number_from_famiport_order_identifier(famiport_refund_entry.famiport_ticket.famiport_order.famiport_order_identifier)),
                unicode(famiport_refund_entry.famiport_ticket.barcode_number),
                unicode(u'-'.join([event_code_1,event_code_2])),
                unicode(rts_helper.format_date(famiport_refund_entry.famiport_ticket.famiport_order.performance_start_at)),
                unicode(famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment.famiport_performance.famiport_event.name_1),
                unicode(famiport_refund_entry.ticket_payment),
                unicode(rts_helper.format_datetime(famiport_refund_entry.refunded_at)),
                unicode(famiport_refund_entry.shop_code),
                unicode(famiport_shop.branch_name if famiport_shop else u''),
            ])

        return {'header':header, 'rows': rows}



