from base64 import b64encode

class Helpers(object):
    def __init__(self, request):
        self.request = request

    def to_data_scheme(self, data):
        return u'data:image/jpeg;base64,' + b64encode(data)
