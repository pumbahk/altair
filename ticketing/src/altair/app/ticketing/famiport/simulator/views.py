# encoding: utf-8
import logging
from io import BytesIO
from datetime import datetime
from lxml import etree
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from altair.app.ticketing.fanstatic import with_bootstrap
from .api import (
    get_communicator,
    get_client_configuration_registry,
    store_payment_result,
    get_payment_result,
    get_payment_result_by_id,
    save_payment_result,
    get_ticket_preview_pictures,
    get_payment_results,
    gen_serial_for_store
    )
from ..communication.models import InfoKubunEnum, ResultCodeEnum, InformationResultCodeEnum
from ..communication.models import ReplyClassEnum

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamiPortTopView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='top', renderer='top.mako')
    def top(self):
        return dict()

    @view_config(route_name='logout')
    def logout(self):
        forget(self.request)
        return HTTPFound(self.request.route_path('top'))

@view_defaults(decorator=with_bootstrap, route_name='select_shop', renderer='select_shop.mako')
class FamiPortSelectShopView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        return dict(store_code=u'', mmk_no=u'', return_url=self.request.params.get('return_url'))

    @view_config(request_method='POST')
    def post(self):
        store_code = self.request.params['store_code']
        mmk_no = self.request.params['mmk_no']
        return_url = self.request.params.get('return_url')
        if len(store_code) != 5:
            self.request.session.flash(u'5文字で入力してください')
            return dict(store_code=store_code, mmk_no=mmk_no, return_url=return_url)
        if len(mmk_no) != 1:
            self.request.session.flash(u'1文字で入力してください')
            return dict(store_code=store_code, mmk_no=mmk_no, return_url=return_url)
        if return_url is None:
            return_url = self.request.route_path('top')
        remember(self.request, '%s:%s' % (store_code, mmk_no))
        return HTTPFound(return_url)


@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamiPortServiceView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='service.index', renderer='services/index.mako')
    def index(self):
        return dict()


@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamiPortReservedServiceSelectionView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='service.reserved', renderer='services/reserved/index.mako')
    def index(self):
        client_configuration_registry = get_client_configuration_registry(self.request)
        return dict(clients=list(client_configuration_registry))

    @view_config(route_name='service.reserved.select')
    def select_service(self):
        client_configuration_registry = get_client_configuration_registry(self.request)
        client = client_configuration_registry.lookup(self.request.params['client_code'])
        if client is not None:
            self.request.session['client_code'] = client.code
            return HTTPFound(self.request.route_path('service.reserved.description'))
        return HTTPFound(self.request.route_path('service.reserved'))


@view_defaults(decorator=with_bootstrap, permission='client_code_provided')
class FamiPortReservedView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def client_configuration(self):
        return client_configuration

    @view_config(route_name='service.reserved.description', renderer='services/reserved/description.mako')
    def index(self):
        return dict()

    @view_config(route_name='service.reserved.info1', renderer='services/reserved/info1.mako')
    def info1(self):
        comm = get_communicator(self.request)
        result = comm.fetch_information(
            type=InfoKubunEnum.Reserved.value,
            store_code=self.context.store_code,
            client_code=self.context.client_code,
            event_code_1=None,
            event_code_2=None,
            performance_code=None,
            sales_segment_code=None,
            reserve_number=None,
            auth_number=None
            )
        message = '???'
        continuable = False
        if result['resultCode'] == InformationResultCodeEnum.NoInformation.value:
            message = None
            continuable = True
        elif result['resultCode'] == InformationResultCodeEnum.WithInformation.value:
            message = result['infoMessage']
            continuable = True
        elif result['resultCode'] == InformationResultCodeEnum.ServiceUnavailable.value:
            message = u'(service unavailable)'
        elif result['resultCode'] == InformationResultCodeEnum.OtherError.value:
            message = u'(other error) %s' % result.get('infoMessage', u'-')
            continuable = True
        return dict(message=message, continuable=continuable)

    @view_config(route_name='service.reserved.entry', renderer='services/reserved/entry.mako')
    def reserve_number_entry(self):
        return dict(reserve_number=u'')

    @view_config(route_name='service.reserved.entry', request_method='POST', renderer='services/reserved/entry.mako')
    def reserve_number_entry_post(self):
        reserve_number = self.request.params['reserve_number']
        if len(reserve_number) != 13:
            self.request.session.flash(u'13文字で入力してください')
            return dict(reserve_number=reserve_number)
        self.request.session['reserve_number'] = reserve_number
        return HTTPFound(self.request.route_path('service.reserved.auth_number_entry'))

    @view_config(route_name='service.reserved.auth_number_entry', renderer='services/reserved/auth_number_entry.mako')
    def auth_number_entry(self):
        if not self.context.client.auth_number_required:
            return HTTPFound(self.request.route_path('service.reserved.inquiry'))
        return dict(auth_number=u'')

    @view_config(route_name='service.reserved.auth_number_entry', request_method='POST', renderer='services/reserved/auth_number_entry.mako')
    def auth_number_entry_post(self):
        auth_number = self.request.params['auth_number']
        if len(auth_number) != 13:
            self.request.session.flash(u'13文字で入力してください')
            return dict(auth_number=auth_number)
        self.request.session['auth_number'] = auth_number
        return HTTPFound(self.request.route_path('service.reserved.info2'))

    @view_config(route_name='service.reserved.info2', renderer='services/reserved/info2.mako')
    def info2(self):
        comm = get_communicator(self.request)
        result = comm.fetch_information(
            type=InfoKubunEnum.Reserved.value,
            store_code=self.context.store_code,
            client_code=self.context.client_code,
            event_code_1=None,
            event_code_2=None,
            performance_code=None,
            sales_segment_code=None,
            reserve_number=self.request.session.get('reserve_number'),
            auth_number=self.request.session.get('auth_number')
            )
        message = '???'
        continuable = False
        if result['resultCode'] == InformationResultCodeEnum.NoInformation.value:
            message = None
            continuable = True
        elif result['resultCode'] == InformationResultCodeEnum.WithInformation.value:
            message = result['infoMessage']
            continuable = True
        elif result['resultCode'] == InformationResultCodeEnum.ServiceUnavailable.value:
            message = u'(service unavailable)'
        elif result['resultCode'] == InformationResultCodeEnum.OtherError.value:
            message = u'(other error) %s' % result.get('infoMessage', u'-')
            continuable = True
        return dict(message=message, continuable=continuable)

    @view_config(route_name='service.reserved.inquiry', renderer='error.mako')
    def inquiry(self):
        comm = get_communicator(self.request)
        result = comm.inquiry(
            store_code=self.context.store_code,
            ticketing_date=self.context.now,
            reserve_number=self.request.session.get('reserve_number'),
            auth_number=self.request.session.get('auth_number')
            )
        if result['resultCode'] == '00':
            self.request.session['inquiry_result'] = result
            if result['nameInput']:
                return HTTPFound(self.request.route_path('service.reserved.name_entry')) 
            elif result['phoneInput']:
                return HTTPFound(self.request.route_path('service.reserved.tel_entry')) 
            else: 
                return HTTPFound(self.request.route_path('service.reserved.confirmation')) 
        else:
            message = u'エラーが発生しました (%(resultCode)s:%(replyCode)s)' % result
            return dict(message=message)

    @view_config(route_name='service.reserved.name_entry', renderer='services/reserved/name_entry.mako')
    def name_entry(self):
        inquiry_result_dict = self.request.session['inquiry_result']
        if not inquiry_result_dict['nameInput']:
            return HTTPFound(self.request.route_path('service.reserved.tel_entry')) 
        return dict(customer_name=u'')

    @view_config(route_name='service.reserved.name_entry', request_method='POST', renderer='services/reserved/name_entry.mako')
    def name_entry_post(self):
        customer_name = self.request.params['customer_name'].strip()
        if not customer_name:
            self.request.session.flash(u'入力してください')
            return dict(customer_name=customer_name)
        self.request.session['customer_name'] = customer_name
        inquiry_result_dict = self.request.session['inquiry_result']
        if inquiry_result_dict['phoneInput']:
            return HTTPFound(self.request.route_path('service.reserved.tel_entry')) 
        else:
            return HTTPFound(self.request.route_path('service.reserved.confirmation')) 

    @view_config(route_name='service.reserved.tel_entry', renderer='services/reserved/tel_entry.mako')
    def tel_entry(self):
        inquiry_result_dict = self.request.session['inquiry_result']
        if not inquiry_result_dict['phoneInput']:
            return HTTPFound(self.request.route_path('service.reserved.confirmation')) 
        return dict(customer_phone_number=u'')

    @view_config(route_name='service.reserved.tel_entry', request_method='POST', renderer='services/reserved/tel_entry.mako')
    def tel_entry_post(self):
        customer_phone_number = self.request.params['customer_phone_number'].strip()
        if not customer_phone_number:
            self.request.session.flash(u'入力してください')
            return dict(customer_phone_number=customer_phone_number)
        self.request.session['customer_phone_number'] = customer_phone_number
        return HTTPFound(self.request.route_path('service.reserved.confirmation')) 

    @view_config(route_name='service.reserved.confirmation', renderer='services/reserved/confirmation.mako')
    def confirmation(self):
        inquiry_result_dict = self.request.session['inquiry_result']
        return dict(
            type=inquiry_result_dict['replyClass'],
            total_amount=inquiry_result_dict['totalAmount'],
            system_fee=inquiry_result_dict['systemFee'],
            ticket_payment=inquiry_result_dict['ticketPayment'],
            ticketing_fee=inquiry_result_dict['ticketingFee'],
            performance_name=inquiry_result_dict['kogyoName'],
            performance_date=inquiry_result_dict['koenDate'],
            barcode_no=inquiry_result_dict['barCodeNo'],
            ticket_count=inquiry_result_dict['ticketCount'],
            ticket_count_total=inquiry_result_dict['ticketCountTotal'],
            name=inquiry_result_dict['name']
            )

    @view_config(route_name='service.reserved.completion', renderer='services/reserved/completion.mako')
    def completion(self):
        inquiry_result_dict = self.request.session['inquiry_result']
        comm = get_communicator(self.request)
        result = comm.payment(
            store_code=self.context.store_code,
            mmk_no=self.context.mmk_no,
            client_code=self.context.client_code,
            sequence_no=self.context.gen_serial(),
            ticketing_date=self.context.now,
            barcode_no=inquiry_result_dict['barCodeNo'],
            customer_name=self.request.session.get('customer_name'),
            customer_phone_number=self.request.session.get('customer_phone_number'),
            )
        tickets = result.get('ticket', None)
        if tickets is not None:
            if not isinstance(tickets, list):
                tickets = [tickets]
            for ticket in tickets:
                ticket['ticketData'] = etree.tostring(etree.parse(BytesIO(ticket['ticketData'].encode('CP932'))), encoding='unicode')
        if result['resultCode'] == u'00':
            store_payment_result(
                self.request,
                store_code=self.context.store_code,
                mmk_no=self.context.mmk_no,
                client_code=self.context.client_code,
                type=result['replyClass'],
                total_amount=result['totalAmount'],
                system_fee=result['systemFee'],
                ticket_payment=result['ticketPayment'],
                ticketing_fee=result['ticketingFee'],
                order_id=result['orderId'],
                barcode_no=result['barCodeNo'],
                exchange_no=result['exchangeTicketNo'],
                ticketing_start_at=result['ticketingStart'],
                ticketing_end_at=result['ticketingEnd'],
                kogyo_name=result['kogyoName'],
                koen_date=result['koenDate'],
                tickets=tickets
                )

            return dict(
                error=False,
                message=u'正常に入金発券を受け付けました',
                type=result['replyClass'],
                total_amount=result['totalAmount'],
                system_fee=result['systemFee'],
                ticket_payment=result['ticketPayment'],
                ticketing_fee=result['ticketingFee'],
                performance_name=result['kogyoName'],
                performance_date=result['koenDate'],
                order_id=result['orderId'],
                barcode_no=result['barCodeNo'],
                exchange_no=result['exchangeTicketNo'],
                ticket_count=result['ticketCount'],
                ticket_count_total=result['ticketCountTotal'],
                tickets=tickets,
                payment_only=result['replyClass'] == int(ReplyClassEnum.PrepaymentOnly.value)
                )
        else:
            message = u'エラーが発生しました (%(resultCode)s:%(replyCode)s)' % result
            return dict(message=message, error=True)

@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamimaPosIndexView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='pos.index', renderer='pos/index.mako')
    def top(self):
        return dict()


@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamimaPosTicketingView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='pos.ticketing.entry', request_method='GET', renderer='pos/ticketing/entry.mako')
    def entry(self):
        return dict(barcode_no=u'')

    @view_config(route_name='pos.ticketing.entry', request_method='POST', renderer='pos/ticketing/entry.mako')
    def entry_post(self):
        barcode_no = self.request.params.get('barcode_no', u'')
        if len(barcode_no) != 13:
            self.request.session.flash(u'13文字で入力してください')
            return dict(barcode_no=barcode_no)

        payment_result = get_payment_result(
            self.request, 
            store_code=self.context.store_code,
            barcode_no=barcode_no
            )
        if payment_result is None:
            self.request.session.flash(u'引換票番号または払込票番号に該当する予約がみつかりません')
            return dict(barcode_no=barcode_no)

        self.request.session['payment_result'] = payment_result.to_dict()

        return HTTPFound(self.request.route_path('pos.ticketing.confirmation'))

    @view_config(route_name='pos.ticketing.confirmation', renderer='pos/ticketing/confirmation.mako')
    def confirmation(self):
        payment_result_dict = self.request.session['payment_result']
        payment_result_dict.update(
            payment_only=payment_result_dict['type'] == int(ReplyClassEnum.PrepaymentOnly.value)
            )
        return payment_result_dict

    @view_config(route_name='pos.ticketing.completion', renderer='pos/ticketing/completion.mako')
    def completion(self):
        payment_result_dict = self.request.session['payment_result']
        comm = get_communicator(self.request)
        images = None
        result = comm.complete(
            store_code=self.context.store_code,
            mmk_no=self.context.mmk_no,
            ticketing_date=self.context.now,
            sequence_no=self.context.gen_serial(),
            client_code=payment_result_dict['client_code'],
            order_id=payment_result_dict['order_id'],
            barcode_no=payment_result_dict['valid_barcode_no'],
            total_amount=payment_result_dict['total_amount']
            )
        if result['resultCode'] == u'00':
            payment_result = get_payment_result(
                self.request, 
                store_code=payment_result_dict['store_code'],
                barcode_no=payment_result_dict['valid_barcode_no']
                )
            if payment_result is None:
                message = u'センター異常です'
            else:
                if payment_result.type == 1:
                    payment_result.paid_at = payment_result.issued_at = self.context.now
                elif payment_result.type == 2:
                    payment_result.paid_at = self.context.now
                elif payment_result.type == 3:
                    if payment_result.paid_at is None:
                        payment_result.paid_at = self.context.now
                    elif payment_result.issued_at is None:
                        payment_result.issued_at = self.context.now
                elif payment_result.type == 4:
                    if payment_result.issued_at is None:
                        payment_result.issued_at = self.context.now
                save_payment_result(self.request, payment_result)
                images = get_ticket_preview_pictures(
                    self.request,
                    discrimination_code='5',
                    client_code=payment_result_dict['client_code'],
                    order_id=payment_result_dict['order_id'],
                    barcode_no=payment_result_dict['valid_barcode_no'],
                    name=u'name',
                    member_id=u'member_id',
                    address_1=u'住所1',
                    address_2=u'住所2',
                    identify_no=u'XXXX',
                    tickets=payment_result_dict['tickets'],
                    response_image_type='jpeg'
                    )
                message = u'正常に入金・発券できました'
        else:
            message = u'エラーが発生しました (%(resultCode)s:%(replyCode)s)' % result
        return dict(message=message, images=images)


@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamimaPosRefundView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='pos.refund.entry', request_method='GET', renderer='pos/refund/entry.mako')
    def entry(self):
        return dict(barcode_no_list=[u'', u'', u'', u''])

    @view_config(route_name='pos.refund.entry', request_method='POST', renderer='pos/refund/entry.mako')
    def entry_post(self):
        barcode_no_list = self.request.params.getall('barcode_no')
        _barcode_no_list = [barcode_no for barcode_no in barcode_no_list if barcode_no]
        if any(len(barcode_no) != 13 for barcode_no in _barcode_no_list):
            self.request.session.flash(u'13文字で入力してください')
            return dict(barcode_no_list=_barcode_no_list + [u''] * (4 - len(_barcode_no_list)))

        comm = get_communicator(self.request)
        result = comm.refund_inquiry(
            store_code=self.context.store_code,
            pos_no=self.context.pos_no,
            timestamp=self.context.now,
            barcodes=barcode_no_list
            )
        self.request.session['refund_inquiry_result'] = result
        return HTTPFound(self.request.route_path('pos.refund.confirmation'))

    @view_config(route_name='pos.refund.confirmation', renderer='pos/refund/confirmation.mako')
    def confirmation(self):
        refund_inquiry_result_dict = self.request.session['refund_inquiry_result']
        return refund_inquiry_result_dict

    @view_config(route_name='pos.refund.completion', renderer='pos/refund/completion.mako')
    def completion(self):
        refund_inquiry_result_dict = self.request.session['refund_inquiry_result']
        comm = get_communicator(self.request)
        result = comm.refund_settlement(
            store_code=self.context.store_code,
            pos_no=self.context.pos_no,
            timestamp=self.context.now,
            barcodes=[entry['barCodeNo'] for entry in refund_inquiry_result_dict['entries'] if entry['resultCode'] == u'00']
            )
        del self.request.session['refund_inquiry_result']
        return {}

@view_defaults(decorator=with_bootstrap)
class FDCCenterView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='fdccenter.service.index', renderer='fdc-center/index.mako')
    def service_index(self):
        return dict()

@view_defaults(decorator=with_bootstrap)
class FDCCenterTransactionServiceView(object):
    cancel_code_list = [
      (u'01', u'券面XML不正'),
      (u'02', u'仮取引ログ出力失敗'),
      (u'03', u'アプリエラー (DBエラー)'),
      (u'04', u'アプリエラー (ミドルウェアエラー)'),
      (u'05', u'アプリエラー (予期しないエラー)'),
      (u'10', u'30分VOID'),
      ]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='fdccenter.service.transaction.index', renderer='fdc-center/service/transaction/index.mako')
    def index(self):
        orders = get_payment_results(self.request)
        return dict(orders=orders, cancel_code_list=self.cancel_code_list)


    @view_config(route_name='fdccenter.service.transaction.cancel', request_method='POST')
    def cancel(self):
        cancel_code = self.request.params['cancel_code']
        order_id_list = self.request.params.getall('order_id')
        orders = [get_payment_result_by_id(self.request, int(order_id)) for order_id in order_id_list]
        for order in orders:
            assert order is not None
            comm = get_communicator(self.request)
            result = comm.cancel(
                store_code=order.store_code,
                mmk_no=order.mmk_no,
                ticketing_date=self.context.now,
                sequence_no=gen_serial_for_store(self.request, self.context.now, order.store_code),
                client_code=order.client_code,
                barcode_no=order.barcode_no,
                order_id=order.order_id,
                cancel_code=cancel_code
                )
            if result['resultCode'] != u'00':
                self.request.session.flash(u'[%s] エラーが発生しました (%s-%s)' % (order.id, result['resultCode'], result['replyCode']))
            else:
                order.voided_at = self.context.now
                save_payment_result(self.request, order)
                self.request.session.flash(u'[%s] 取消送信しました' % order_id)
        return HTTPFound(self.request.route_path('fdccenter.service.transaction.index'))

