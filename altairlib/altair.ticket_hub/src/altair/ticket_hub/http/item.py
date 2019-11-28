import xmltodict

from base import TicketHubRequest, TicketHubResponse

class TicketHubItemListRequest(TicketHubRequest):
    def __init__(self, facility_code, agent_code, item_group_code):
        self.response_class = TicketHubItemListResponse
        self.method = 'GET'
        self.base_path = '/items/{}/{}/{}'.format(facility_code, agent_code, item_group_code)

    def path(self):
        return self.base_path

    def params(self):
        return None

class TicketHubItemResponse(object):
    def __init__(self, code, name, price, sale_limit, grouping_qty, ticket_code, ticket_name, ticket_price):
        self.code = code
        self.name = name
        self.price = price
        self.sale_limit = sale_limit
        self.grouping_qty = grouping_qty
        self.ticket_code = ticket_code
        self.ticket_name = ticket_name
        self.ticket_price = ticket_price

    @classmethod
    def from_raw_resonse(cls, raw):
        ticket = raw['unit_item_info_list']['unit_item_info']
        return cls(
            code=raw['item_code'],
            name=raw['item_name'],
            price=raw['item_price_in_tax'],
            sale_limit=raw['user_sale_limit'],
            grouping_qty=raw['grouping_qty'],
            ticket_code=ticket['ticket_code'],
            ticket_name=ticket['ticket_name'],
            ticket_price=ticket['ticket_price_in_tax']
        )

class TicketHubItemListResponse(TicketHubResponse):
    def __init__(self, items, facility_code, agent_code, item_group_code, requested_at):
        self.items = items
        self.facility_code = facility_code
        self.agent_code = agent_code
        self.item_group_code = item_group_code
        self.requested_at = requested_at

    @classmethod
    def build(cls, raw):
        res_dict = xmltodict.parse(raw)
        requested_at = res_dict['response_set']['header']['input_date_time']
        body = res_dict['response_set']['body']
        item_group_code = body['item_group_info_list']['item_group_info']['item_group_code']
        raw_items = body['item_group_info_list']['item_group_info']['item_info_list']['item_info']
        items = map(TicketHubItemResponse.from_raw_resonse, raw_items)
        return cls(
            items=items,
            facility_code=body['facility_code'],
            agent_code=body['agent_code'],
            item_group_code=item_group_code,
            requested_at=requested_at
        )