class SelectAuthTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        if not (hasattr(request.context, 'membership') and request.context.membership):
            request.environ['ticketing.cart.rakuten_auth.required'] = True

        return self.handler(request)
