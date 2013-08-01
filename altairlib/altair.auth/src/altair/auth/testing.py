class DummyDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        return self.request.testing_who_api_name

class DummySession(dict):
    def save(self):
        pass
