import logging
from ticketing.users.models import Membership
from ticketing.models import DBSession
from ticketing.core import api as core_api

logger = logging.getLogger(__name__)

def get_memberships(request):
    if hasattr(request, 'context') and hasattr(request.context, 'memberships'):
        logger.info('memberships retrieved from context')
        return request.context.memberships
    else:
        logger.info('memberships retrieved directly')
        return Membership.query.filter_by(organization_id=request.organization.id).all()

def login_url(request):
    organization = core_api.get_organization(request)
    memberships = DBSession.query(Membership).filter_by(organization_id=organization.id).all()
    logger.debug("login url %s membership %s" % (request.context, memberships))
    url = request.route_url('fc_auth.login', membership=memberships[0].name)
    logger.debug("login url %s" % url)
    return url 

