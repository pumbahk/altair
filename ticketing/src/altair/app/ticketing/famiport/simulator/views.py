# encoding: utf-8
import logging
from datetime import datetime
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from altair.app.ticketing.fanstatic import with_bootstrap
from .api import get_communicator, get_client_configuration_registry, store_payment_result, get_payment_result, save_payment_result, get_ticket_preview_pictures
from ..communication.models import InfoKubunEnum, ResultCodeEnum, InformationResultCodeEnum

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
                return HTTPFound(self.request.route_path('service.reserved.phone_entry')) 
            else: 
                return HTTPFound(self.request.route_path('service.reserved.confirmation')) 
        else:
            message = u'エラーが発生しました (%(resultCode)s:%(replyCode)s)' % result
            return dict(message=message)

    @view_config(route_name='service.reserved.confirmation', renderer='services/reserved/confirmation.mako')
    def confirmation(self):
        inquiry_result = self.request.session['inquiry_result']
        return dict(
            total_amount=inquiry_result['totalAmount'],
            system_fee=inquiry_result['systemFee'],
            ticket_payment=inquiry_result['ticketPayment'],
            ticketing_fee=inquiry_result['ticketingFee'],
            performance_name=inquiry_result['kogyoName'],
            performance_date=inquiry_result['koenDate'],
            barcode_no=inquiry_result['barCodeNo'],
            ticket_count=inquiry_result['ticketCount'],
            ticket_count_total=inquiry_result['ticketCountTotal'],
            name=inquiry_result['name']
            )

    @view_config(route_name='service.reserved.completion', renderer='services/reserved/completion.mako')
    def completion(self):
        inquiry_result = self.request.session['inquiry_result']
        comm = get_communicator(self.request)
        result = comm.payment(
            store_code=self.context.store_code,
            mmk_no=self.context.mmk_no,
            client_code=self.context.client_code,
            sequence_no=self.context.gen_serial(),
            ticketing_date=self.context.now,
            barcode_no=inquiry_result['barCodeNo'],
            customer_name=self.request.session.get('customer_name'),
            customer_phone_number=self.request.session.get('customer_phone_number'),
            )
        tickets = result.get('ticket', None)
        if tickets is not None and not isinstance(tickets, list):
            tickets = [tickets]

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
                tickets=tickets
                )
        else:
            message = u'エラーが発生しました (%(resultCode)s:%(replyCode)s)' % result
            return dict(message=message, error=True)

@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamimaPosView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='pos.index', renderer='pos/index.mako')
    def top(self):
        return dict()

    @view_config(route_name='pos.entry', request_method='GET', renderer='pos/entry.mako')
    def entry(self):
        return dict(barcode_no=u'')

    @view_config(route_name='pos.entry', request_method='POST', renderer='pos/entry.mako')
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
    def ticketing_confirmation(self):
        return self.request.session['payment_result']

    @view_config(route_name='pos.ticketing.completion', renderer='pos/ticketing/completion.mako')
    def ticketing_completion(self):
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
            barcode_no=payment_result_dict['barcode_no'],
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
