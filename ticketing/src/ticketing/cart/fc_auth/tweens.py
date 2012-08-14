from .api import login_url

class FCAuthTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):

        if hasattr(request.context, 'membership') and request.context.membership:
            request.environ['ticketing.cart.fc_auth.required'] = True
            request.environ['ticketing.cart.fc_auth.membership'] = request.context.membership
            request.environ['ticketing.cart.fc_auth.login_url'] = login_url(request)
