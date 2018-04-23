# encoding: utf-8

from pyramid.security import ACLAllowed
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from altair.aes_urlsafe import AESURLSafe
from altair.restful_framework.permissions import BasePermission

from altair.app.ticketing.core.models import Performance, Event, Organization

class ResaleAPIKeyPermission(BasePermission):
    def __init__(self):
        super(ResaleAPIKeyPermission, self).__init__()
        self.aes = AESURLSafe(key="ALTAIR_AES_ENCRYPTION_FOR_RESALE")

    def has_permission(self, request, view):
        key = request.headers.get('Resale-API-Key', None)
        if not key:
            return False
        try:
            return self.aes.decrypt(key) == u'request_from_orion_server'
        except Exception:
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ResaleAltairPermission(BasePermission):

    def has_permission(self, request, view):
        return isinstance(
            request.has_permission(
                'event_viewer', request.context),
            ACLAllowed
        )

    def has_object_permission(self, request, view, obj):
        if type(obj) == 'ResaleSegment':
            performance_id = obj.performance_id
        elif type(obj) == 'ResaleRequest':
            performance_id = obj.resale_segment.performance_id
        else:
            return False
        try:
            organization = view.dbsession.query(Organization.id)\
                .join(Event, Performance)\
                .filter(Performance.id == performance_id)\
                .one()

            return organization.id == request.context.organization.id
        except (NoResultFound, MultipleResultsFound, AttributeError):
            return False