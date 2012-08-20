import logging

logger = logging.getLogger(__name__)

def login_url(request):
    membership = request.context.membership
    logger.debug("login url %s membership %s" % (request.context, membership))
    return request.route_url('fc_auth.login', membership=membership.name)

