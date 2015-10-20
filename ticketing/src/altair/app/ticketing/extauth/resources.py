# encoding: utf-8
from pyramid.security import Everyone, Allow, Authenticated, DENY_ALL
from pyramid.decorator import reify
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound
from .models import MemberSet, MemberKind

class ExtAuthBase(object):
    __acl__ = [
        (Allow, 'altair.auth.authenticator:rakuten', 'rakuten'),
        (Allow, Authenticated, 'authenticated'),
        DENY_ALL,
        ]

class ExtAuthRoot(ExtAuthBase):
    subtype = None

    def __init__(self, request):
        self.request = request

    def __getitem__(self, subtype):
        return ExtAuthSubTypeResource(self.request, subtype)

class ExtAuthSubTypeResource(ExtAuthBase):
    def __init__(self, request, subtype):
        self.request = request
        self.subtype = subtype

    @reify
    def member_sets(self):
        dbsession = get_db_session(self.request, 'extauth_slave')
        return dbsession.query(MemberSet) \
            .filter(MemberSet.organization_id == self.request.organization.id) \
            .filter((MemberSet.applicable_subtype == self.subtype)
                    |(MemberSet.applicable_subtype == None)) \
            .all()

    def route_path(self, *args, **kwargs):
        return self.request.route_path(*args, subtype=self.subtype, **kwargs)
    
    def route_url(self, *args, **kwargs):
        return self.request.route_url(*args, subtype=self.subtype, **kwargs)
