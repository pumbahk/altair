from pyramid.decorator import reify
from altair.sqlahelper import get_db_session
from altair.app.ticketing.cart.api import get_organization
from altair.app.ticketing.users.models import Membership

class FCAuthResourceBase(object):
    def __init__(self, request):
        self.request = request

    @reify
    def organization(self):
        return get_organization(self.request)

    @reify
    def primary_membership(self):
        session = get_db_session(self.request, 'slave')
        return session.query(Membership) \
            .filter_by(organization_id=self.organization.id) \
            .first()

    @reify
    def available_memberships(self):
        session = get_db_session(self.request, 'slave')
        return session.query(Membership) \
            .filter_by(organization_id=self.organization.id) \
            .all()

    def lookup_membership(self, membership_name):
        session = get_db_session(self.request, 'slave')
        return session.query(Membership) \
            .filter_by(organization_id=self.organization.id,
                       name=membership_name) \
            .one()

class FixedMembershipFCAuthResource(FCAuthResourceBase):
    def __init__(self, request, membership_name):
        super(FixedMembershipFCAuthResource, self).__init__(request)
        self._membership_name = membership_name

    @reify
    def membership(self):
        return Membership.query \
            .filter_by(organization_id=self.organization.id) \
            .filter_by(name=self._membership_name) \
            .first()

class FCAuthResource(FCAuthResourceBase):
    def __init__(self, request):
        super(FCAuthResource, self).__init__(request)

def fc_auth_resource_factory(request):
    membership_name = request.matchdict['membership']
    if membership_name == '-':
        return FCAuthResource(request)
    else:
        return FixedMembershipFCAuthResource(request, membership_name)
