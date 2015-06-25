from pyramid.security import Allow, Deny, Authenticated, DENY_ALL
from pyramid.decorator import reify
from ..models import FamiPortPerformance
from altair.sqlahelper import get_db_session

class BaseResource(object):
    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'administrator', 'administrator'),
        (Allow, 'administrator', 'operator'),
        (Allow, 'operator', 'operator'),
        DENY_ALL,
        ]

    def __init__(self, request):
        self.request = request


class TopResource(BaseResource):
    pass


class ExampleResource(BaseResource):
    pass

class SearchResource(BaseResource):
    pass

class DetailBaseResource(BaseResource):
    pass

class PerformanceDetailResource(DetailBaseResource):
    def __init__(self, request):
        self.request = request
        fami_session = get_db_session(self.request, 'famiport')
        performance_id = self.request.matchdict.get('performance_id')
        if performance_id:
            self.performance = fami_session.query(FamiPortPerformance)\
                                .filter(FamiPortPerformance.id==performance_id)\
                                .one()
