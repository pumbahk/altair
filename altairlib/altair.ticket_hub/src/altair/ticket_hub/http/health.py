import xmltodict
from base import TicketHubRequest, TicketHubResponse

class TicketHubHealthRequest(TicketHubRequest):
    def __init__(self):
        self.response_class = TicketHubHealthResponse
        self.method = 'GET'
        self.base_path = '/healths'

    def path(self):
        return self.base_path
    def params(self):
        return None

class TicketHubHealthResponse(TicketHubResponse):
    @classmethod
    def build(cls, raw):
        res_dict = xmltodict.parse(raw)
        print(res_dict['response_set'])