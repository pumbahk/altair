import xmltodict
import logging
from base import TicketHubRequest, TicketHubResponse, parse_datetime_str

logger = logging.getLogger(__name__)


class TicketHubCreateTempOrderRequest(TicketHubRequest):
    def __init__(self, cart_id, seller_order_no=None, expire_date_time=None):
        self.response_class = TicketHubCreateTempOrderResponse
        self.method = 'PATCH'
        self.base_path = '/carts/{}/auths'.format(cart_id)
        self.seller_order_no = seller_order_no
        self.expire_date_time = expire_date_time

    def path(self):
        return self.base_path

    def _optional_params(self, base):
        if self.seller_order_no:
            base['seller_order_no'] = self.seller_order_no
        if self.expire_date_time:
            base['expire_date_time'] = self.expire_date_time
        return base

    def params(self):
        base = dict(
            request_set=dict(
                body=dict()
            )
        )
        return self._optional_params(base)


class TicketHubOrderedTicketResponse(object):
    def __init__(self, item_group_code, item_code, item_amount, ticket_code, ticket_qr_code, ticket_qr_binary, ticket_id):
        self.item_group_code = item_group_code
        self.item_code = item_code
        self.item_amount = item_amount
        self.ticket_code = ticket_code
        self.ticket_qr_code = ticket_qr_code
        self.ticket_qr_binary = ticket_qr_binary
        self.ticket_id = ticket_id

    @classmethod
    def from_item_info_response(cls, item_group_info):
        tickets = []
        for group in item_group_info:
            for item in group['item_info_list']['item_info']:
                for ticket in item['ticket_info_list']['ticket_info']:
                    tickets.append(
                        cls(
                            item_group_code=group['item_group_code'],
                            item_code=item['item_code'],
                            item_amount=item['item_price_in_tax'],
                            ticket_code=ticket['ticket_code'],
                            ticket_qr_code=ticket['ticket_qr_code'],
                            ticket_qr_binary=ticket['ticket_qr_binary'],
                            ticket_id=ticket['disp_ticket_id']
                        )
                    )
        return tickets

class TicketHubCreateTempOrderResponse(TicketHubResponse):
    def __init__(self, order_no, purchase_no, purchase_qr_code, total_amount, tickets, requested_at):
        self.order_no = order_no
        self.purchase_no=purchase_no
        self.purchase_qr_code = purchase_qr_code
        self.total_amount = total_amount
        self.tickets = tickets
        self.requested_at = requested_at

    @classmethod
    def build(cls, raw):
        res_dict = xmltodict.parse(raw, force_list=('item_group_info', 'item_info', 'ticket_info'))
        logger.info('[TicketHubCreateTempOrderResponse] : %s', res_dict)
        requested_at = res_dict['response_set']['header']['input_date_time']
        body = res_dict['response_set']['body']
        return cls(
            order_no=body['order_no'],
            purchase_no=body['disp_purchase_no'],
            purchase_qr_code=body['purchase_qr_code'],
            total_amount=body['order_total_sum'],
            tickets=TicketHubOrderedTicketResponse.from_item_info_response(body['item_group_info_list']['item_group_info']),
            requested_at=parse_datetime_str(requested_at)
        )

    @property
    def total_ticket_quantity(self):
        return len(self.tickets)

class TicketHubCompleteTempOrderRequest(TicketHubRequest):
    def __init__(self, order_no, payment_datetime=None):
        self.response_class = TicketHubCompleteTempOrderResponse
        self.method = 'PATCH'
        self.base_path = '/auths/{}/orders'.format(order_no)
        self.payment_datetime = payment_datetime

    def params(self):
        return None

    def path(self):
        return self.base_path

class TicketHubCompleteTempOrderResponse(TicketHubResponse):
    def __init__(self, order_no, order_date, order_time, requested_at):
        self.order_no = order_no
        self.order_date = order_date # yyyyMMdd
        self.order_time = order_time # hhmmss
        self.requested_at = requested_at

    @classmethod
    def build(cls, raw):
        res_dict = xmltodict.parse(raw)
        logger.info('[TicketHubCompleteTempOrderResponse] : %s', res_dict)
        requested_at = res_dict['response_set']['header']['input_date_time']
        body = res_dict['response_set']['body']
        return cls(
            order_no=body['order_no'],
            order_date=body['order_date'],
            order_time=body['order_time'],
            requested_at=parse_datetime_str(requested_at)
        )
