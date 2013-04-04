# This package may contain traces of nuts
from pyramid.httpexceptions import HTTPBadRequest

def includeme(config):
    config.add_tween(__name__ + '.EncodingFixerTween')


class EncodingFixerTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry


    def __call__(self, request):
        try:
            request.path_info
            request.GET
        except UnicodeError:
            return HTTPBadRequest()
        else:
            return self.handler(request)
        
