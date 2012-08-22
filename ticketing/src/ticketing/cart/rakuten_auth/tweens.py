
class RakutenAuthTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        try:
            return self.handler(request)
        finally:

            if hasattr(request, 'context'):
                if not hasattr(request.context, 'membership') or not request.context.membership:
                    request.environ['ticketing.cart.rakuten_auth.required'] = True

