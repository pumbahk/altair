from datetime import datetime


class TicketHubRequest(object):
    def path(self):
        pass

    def params(self):
        pass

    def build_response(self, raw):
        return self.response_class.build(raw)


class TicketHubResponse(object):
    @classmethod
    def parse(cls, raw):
        pass


def parse_datetime_str(str):
    return datetime.strptime(str.replace('+09:00', ''), '%Y-%m-%dT%H:%M:%S')
