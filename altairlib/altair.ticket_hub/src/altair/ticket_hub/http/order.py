import xmltodict
from base import TicketHubRequest, TicketHubResponse

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
        requested_at = res_dict['response_set']['header']['input_date_time']
        body = res_dict['response_set']['body']
        return cls(
            order_no=body['order_no'],
            purchase_no=body['disp_purchase_no'],
            purchase_qr_code=body['purchase_qr_code'],
            total_amount=body['order_total_sum'],
            tickets=TicketHubOrderedTicketResponse.from_item_info_response(body['item_group_info_list']['item_group_info']),
            requested_at=requested_at
        )

    @property
    def total_ticket_quantity(self):
        return len(self.tickets)

class TicketHubCreateOrderRequest(TicketHubRequest):
    def path(self):
        pass
    def params(self):
        pass

# "body": {
#     "facility_code": "00290",
#     "agent_code": "9012",
#     "order_no": "06006001100000006224",
#     "purchase_no": "0029020191007810000100004",
#     "disp_purchase_no": "00290-2019-1007-8100-0010-0004",
#     "purchase_qr_code": "20191007020100004000000000980010000000000",
#     "purchase_qr_binary": "iVBORw0KGgoAAAANSUhEUgAAAMgAAADIAQAAAACFI5MzAAAAyUlEQVR42t2YWw4EIQgE+/6XZmMQaMxcoBaTmUj5Q3gISikRcT46awuNxBGl/oC4GixRKsbS0ZJJ/pL+AbmqD0tpJCPxwo8YhZFbFWw9NYRFoiQ3tmeSsi/GhzsqYcS27rx9kES6LFglDzDp4u3VPEQl5jq3dDsVRKJySt0L7cMwourrxokhMFlrYlFUormVOqUEJnblqjKNTHzS865VVGINUc9IaGKTRDnsdkZkEj2LT86RiSy91vSKI49qdw08UqV7ZtbnPQtFfpQ3Dn9aPyg2AAAAAElFTkSuQmCC",
#     "order_date": "20191007",
#     "order_time": "042450",
#     "order_state": "1",
#     "order_total_sum": "2000",
#     "order_total_qty": "1",
#     "item_group_info_list": {
#         "item_group_info": {
#             "item_group_code": "0001",
#             "program_code": null,
#             "item_info_list": {
#                 "item_info": {
#                     "item_code": "01001",
#                     "set_ticket_divi": "0",
#                     "item_price_in_tax": "2000",
#                     "ticket_info_list": {
#                         "ticket_info": {
#                             "ticket_code": "01001",
#                             "ticket_qr_code": "20191007020100001000000000980010100000000",
#                             "ticket_id": "0029020191007810000100011",
#                             "disp_ticket_id": "00290-2019-1007-8100-0010-0011",
#                             "ticket_state": "1",
#                             "usage_valid_start_date": "20191007",
#                             "ticket_print_divi": "1",
#                             "ticket_qr_binary": "iVBORw0KGgoAAAANSUhEUgAAAMgAAADIAQAAAACFI5MzAAAAyUlEQVR42t2YWw7DIAwE9/6Xdttg1kvEBaYQkYjhZ+UXjrRG/YbWPAeNeO+7Pq/ewRLtDYVWPrHg/yBr86aURpbEJVYXH4WRzgoxXzmERcpDXur8QhF7YaAOLybRS5j6PJVURfY7/BFJ2kIOKBddKBl9lUqfh0hqUxsxD/HINllUJxcpIukLQ+n0TVGJPXEQmkSdlSMNTDSOGOas7AFZpOa+MPWJTBRpuw1WWX+ZZPLFxByZKMOrzh6QRdzp2QktnEiOTu/2PwtFPoABDn8Dj377AAAAAElFTkSuQmCC"
#                         }
#                     },
#                     "item_qty": "1",
#                     "item_sum": "2000"
#                 }
#             }
#         }
# }