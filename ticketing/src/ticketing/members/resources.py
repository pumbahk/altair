from pyramid.interfaces import IRootFactory
from pyramid.decorator import reify
from ticketing.users.models import Membership, MemberGroup


class MembersResource(object):
    __name__ = 'tickets'

    ## too-bad
    def __init__(self, request):
        self.request = request
        parent = self.request.registry.getUtility(IRootFactory)(self.request)

        if not hasattr(self, "__acl__") and parent and hasattr(parent, "__acl__"):
            self.__acl__ = parent.__acl__
        self.user = parent.user
        
    @property
    def memberships(self):
        return Membership.query.filter_by(organization_id = self.user.organization_id)

    @reify
    def membership(self):
        return Membership.query.filter_by(organization_id = self.user.organization_id, 
                                          id = self.request.matchdict["membership_id"]).first()

    @property
    def membergroups(self):
        return MemberGroup.query.filter_by(membership_id = self.request.matchdict["membership_id"])
