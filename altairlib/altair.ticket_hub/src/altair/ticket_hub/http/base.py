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