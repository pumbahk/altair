from pyramid.interfaces import IRootFactory
from pyramid.decorator import reify
from altair.app.ticketing.users.models import Membership, MemberGroup
from altair.app.ticketing.resources import TicketingAdminResource

class MembersResource(TicketingAdminResource):
    __name__ = 'tickets'

    @property
    def memberships(self):
        return Membership.query.filter_by(organization_id = self.user.organization_id)

    @reify
    def membership(self):
        return Membership.query.filter_by(organization_id = self.user.organization_id, 
                                          ).first()

    @property
    def membergroups(self):
        return MemberGroup.query.filter_by(membership_id = self.request.matchdict["membership_id"])
