class FCAuthResource(object):
    def __init__(self, request):
        self.request = request


    @property
    def membership(self):
        return self.request.matchdict.get('membership')

