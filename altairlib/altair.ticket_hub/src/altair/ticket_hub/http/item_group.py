import xmltodict
from base import TicketHubRequest, TicketHubResponse

class TicketHubItemGroupRequest(TicketHubRequest):
    def __init__(self, facility_code, agent_code):
        self.response_class = TicketHubItemGroupResponse
        self.method = 'GET'
        self.base_path = '/item-groups/{}/{}'.format(facility_code, agent_code)

    def path(self):
        return self.base_path
    def params(self):
        return None

class TicketHubItemGroupResponse(TicketHubResponse):
    def __init__(self, code, name, facility_code, agent_code, requested_at):
        self.code = code
        self.name = name
        self.facility_code = facility_code
        self.agent_code = agent_code
        self.requested_at = requested_at

    @classmethod
    def build(cls, raw):
        res_dict = xmltodict.parse(raw)
        requested_at = res_dict['response_set']['header']['input_date_time']
        body = res_dict['response_set']['body']
        item = body['category_info_list']['category_info']['item_group_info_list']['item_group_info']
        return cls(
            code = item['item_group_code'],
            name = item['item_group_name'],
            facility_code = body['facility_code'],
            agent_code = body['agent_code'],
            requested_at = requested_at
        )