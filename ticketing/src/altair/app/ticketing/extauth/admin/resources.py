from pyramid.security import Allow, Everyone, Authenticated, authenticated_userid
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden, HTTPNotFound
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound
from ..models import Organization
from models import Role, Permission, Operator

class ExtauthAdminResource(object):
    _base_acl = [
        (Allow, Everyone, 'everybody'),
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'login', 'everybody'),
    ]

    # the same ACL is applied to every resource under.
    @reify
    def __acl__(self):
        acl = self._base_acl[:]
        roles = self.db_session.query(Role).all()
        for role in roles:
            for permission in role.permissions:
                acl.append((Allow, role.name, permission.category_name))
        return acl

    def __init__(self, request):
        self.request = request
        self.db_session = get_db_session(self.request, 'extauth_slave')

class OrganizationCollectionResource(ExtauthAdminResource):
    def __getitem__(self, organization_id_str):
        try:
            organization_id = long(organization_id_str)
            resource = OrganizationResource(self.request, organization_id=organization_id)
            if self.request.has_permission('administration', self) or \
                    (self.request.has_permission('manage_organization', self) and resource.my_organization):
                return resource
            else:
                raise HTTPForbidden
        except (TypeError, ValueError):
            raise HTTPForbidden()


class OrganizationResource(ExtauthAdminResource):
    def __init__(self, request, organization_id):
        super(OrganizationResource, self).__init__(request)
        try:
            self.organization = self.db_session.query(Organization).filter_by(id=organization_id).one()
        except NoResultFound:
            raise HTTPNotFound()

    @reify
    def my_organization(self):
        return self.organization.id == self.request.operator.organization_id
