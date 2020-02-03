import xmltodict
from base import TicketHubRequest, TicketHubResponse, parse_datetime_str

class TicketHubFacilityRequest(TicketHubRequest):
    def __init__(self, id):
        self.response_class = TicketHubFacilityResponse
        self.method = 'GET'
        self.base_path = '/facilities/{}'.format(id)

    def path(self):
        return self.base_path
    def params(self):
        return None

class TicketHubFacilityResponse(TicketHubResponse):
    def __init__(self, requested_at, code, name, post_code, address1, address2, address3, tel, mail_address, **kwargs):
        super(TicketHubResponse, self).__init__(**kwargs)
        self.requested_at = requested_at
        self.code = code
        self.name = name
        self.post_code = post_code
        self.address1 = address1
        self.address2 = address2
        self.address3 = address3
        self.tel = tel
        self.mail_address = mail_address

    @classmethod
    def build(cls, raw):
        res_dict = xmltodict.parse(raw)
        requested_at = res_dict['response_set']['header']['input_date_time']
        data = res_dict['response_set']['body']['facility_info_list']['facility_info']
        return cls(
            requested_at=parse_datetime_str(requested_at),
            code=data['facility_code'],
            name=data['facility_name'],
            post_code=data['post_code'],
            address1=data['address1'],
            address2=data['address2'],
            address3=data['address3'],
            tel=data['tel'],
            mail_address=data['mail_address']
        )