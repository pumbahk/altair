from pyramid.security import Allow, Deny, Authenticated, DENY_ALL
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden, HTTPNotFound
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound
from ..models import Organization


class BaseResource(object):
    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'administrator', 'manage_my_organization'),
        (Allow, 'administrator', 'manage_operators'),
        (Allow, 'administrator', 'manage_oauth_clients'),
        (Allow, 'administrator', 'manage_member_sets'),
        (Allow, 'administrator', 'manage_member_kinds'),
        (Allow, 'administrator', 'manage_members'),
        (Allow, 'operator', 'manage_members'),
        (Allow, 'operator', 'manage_member_kinds'),
        DENY_ALL,
        ]

    def __init__(self, request):
        self.request = request


class OrganizationCollectionResource(BaseResource):
    def __getitem__(self, organization_id_str):
        try:
            organization_id = long(organization_id_str)
        except (TypeError, ValueError):
            pass
        resource = OrganizationResource(self.request, organization_id)
        if not self.request.has_permission('manage_organizations', context=self):
            if not self.request.has_permission('manage_my_organization', context=self) or \
               resource.organization.id != self.request.operator.organization_id:
                raise HTTPForbidden()
        return resource


class OrganizationResource(BaseResource):
    def __init__(self, request, organization_id):
        super(OrganizationResource, self).__init__(request)
        try:
            self.organization = get_db_session(self.request, 'extauth').query(Organization).filter_by(id=organization_id).one()
        except NoResultFound:
            raise HTTPNotFound()

    @reify
    def my_organization(self):
        return self.organization.id == self.request.operator.organization_id
