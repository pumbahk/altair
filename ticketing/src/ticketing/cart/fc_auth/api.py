import logging

from ticketing.core import api as core_api

logger = logging.getLogger(__name__)

def login_url(request):
    organization = core_api.get_organization(request)
    memberships = organization.memberships
    logger.debug("login url %s membership %s" % (request.context, memberships))
    url = request.route_url('fc_auth.login', membership=memberships[0].name)
    logger.debug("login url %s" % url)
    return url 

