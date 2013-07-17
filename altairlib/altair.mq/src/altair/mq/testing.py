from pyramid import testing


class DummyMessage(testing.DummyResource):
    def __init__(self, channel=None, method=None, header=[], body="", params={}, request=None):
        testing.DummyResource.__init__(self, 
                                       channel=channel, 
                                       method=method, 
                                       header=header, 
                                       body=body, 
                                       params=params)

        if request is None:
            request = testing.DummyRequest()

        self.request = request
