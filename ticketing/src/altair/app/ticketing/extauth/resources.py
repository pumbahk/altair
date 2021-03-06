# encoding: utf-8
import logging
from pyramid.security import Everyone, Allow, Authenticated, DENY_ALL
from pyramid.decorator import reify
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound
from .models import MemberSet, MemberKind, OAuthServiceProvider
from .exceptions import ExtauthSettingError

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

    @property
    def visible_oauth_service_providers(self):
        dbsession = get_db_session(self.request, 'extauth_slave')
        return dbsession.query(OAuthServiceProvider) \
            .filter_by(organization_id=self.request.organization.id) \
            .filter_by(visible=True) \
            .all()

    @property
    def challenge_service_provider_name(self):
        if self.request.params.get('service_provider_name'):
            return self.request.params.get('service_provider_name')
        dbsession = get_db_session(self.request, 'extauth_slave')
        sp = dbsession.query(OAuthServiceProvider) \
            .filter_by(organization_id=self.request.organization.id) \
            .first()
        if not sp:
            raise ExtauthSettingError('need to register at least one OAuthServiceProvider')
        return sp.name
