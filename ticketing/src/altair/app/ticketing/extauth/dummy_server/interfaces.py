from zope.interface import Interface

class IRequestHandler(Interface):
    def handle_request(request):
        pass

    def build_response(request, flavor):
        pass

