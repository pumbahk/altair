import logging

logger = logging.getLogger(__name__)

def login_url(request):
    memberships = request.context.memberships
    logger.debug("login url %s membership %s" % (request.context, memberships))
    return request.route_url('fc_auth.login', membership=memberships[0].name)

