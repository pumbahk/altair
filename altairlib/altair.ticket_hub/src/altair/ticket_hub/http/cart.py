# -*- coding: utf-8 -*-

import xmltodict
import logging
from base import TicketHubRequest, TicketHubResponse, parse_datetime_str

logger = logging.getLogger(__name__)

"""
item_type_divi: 0=通常商品、1=日時指定商品、2=座席指定商品、3=パスポート商品
"""

NORMAL_PRODUCT = 0
DATE_SPECIFIED_PRODUCT = 1
SEAT_SPECIFIED_PRODUCT = 2
PASSPORT_PRODUCT = 3

class TicketHubGetCartRequest(TicketHubRequest):
    def __init__(self, cart_id):
        self.response_class = TicketHubCreateCartResponse
        self.method = 'GET'
        self.base_path = '/carts/{}'.format(cart_id)

    def path(self):
        return self.base_path

    def params(self):
        return None

class TicketHubGetCartResponse(TicketHubResponse):
    def __init__(self, cart_id, requested_at):
        self.cart_id = cart_id
        self.requested_at = requested_at

    @classmethod
    def build(cls, raw):
        res_dict = xmltodict.parse(raw)
        requested_at = res_dict['response_set']['header']['input_date_time']
        body = res_dict['response_set']['body']
        return cls(
            cart_id=body['cart_id'],
            requested_at=parse_datetime_str(requested_at)
        )

# cart_items = [{ "item_group_code" String(5), items: [{ "item_code": String(4), "quantity": Int }] }]

class TicketHubCreateCartRequest(TicketHubRequest):
    def __init__(self, facility_code, agent_code, cart_items):
        self.facility_code = facility_code
        self.agent_code = agent_code
        self.cart_items = cart_items
        self.response_class = TicketHubCreateCartResponse
        self.method = 'POST'
        self.base_path = '/carts'

    def path(self):
        return self.base_path

    def params(self):
        return dict(
            request_set=dict(
                body=dict(
                    facility_code=self.facility_code,
                    agent_code=self.agent_code,
                    item_group_info_list=[dict(
                        item_group_info=dict(
                            item_group_code=group.get("item_group_code"),
                            item_info_list=[dict(
                                item_info=dict(
                                    item_code=item.get("item_code"),
                                    item_type_divi=NORMAL_PRODUCT,
                                    item_qty=item.get("quantity"),
                                    ticket_info_list=[dict(
                                        ticket_info=dict(
                                            option_field_info_list=[dict(
                                                option_field_info=dict(
                                                    field_code="01",
                                                    field_value=""
                                                )
                                            )]
                                        )
                                    )]
                                )
                            ) for item in group.get("items")]
                        )
                    ) for group in self.cart_items]
                )
            )
        )

class TicketHubCreateCartResponse(TicketHubResponse):
    def __init__(self, cart_id, requested_at):
        self.cart_id = cart_id
        self.requested_at = requested_at

    @classmethod
    def build(cls, raw):
        res_dict = xmltodict.parse(raw)
        logger.info('[TicketHubCreateCartResponse] : %s', res_dict)
        requested_at = res_dict['response_set']['header']['input_date_time']
        body = res_dict['response_set']['body']
        return cls(
            cart_id=body['cart_id'],
            requested_at=parse_datetime_str(requested_at)
        )