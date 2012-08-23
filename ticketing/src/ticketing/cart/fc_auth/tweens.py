import logging
from .api import login_url

logger = logging.getLogger(__name__)

class FCAuthTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):

        try:
            return self.handler(request)
        finally:
            if hasattr(request, 'context'):
                logger.debug('fc auth tween %s' % request.context)
                if hasattr(request.context, 'memberships'):
                    logger.debug('check fc_auth membergroups %s' % request.context.membergroups)
                    logger.debug('check fc_auth memberships %s' % request.context.memberships)
                    if request.context.memberships:
                        request.environ['ticketing.cart.fc_auth.required'] = True
                        request.environ['ticketing.cart.fc_auth.login_url'] = login_url(request)
