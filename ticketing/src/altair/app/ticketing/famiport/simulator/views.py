# encoding: utf-8
from pyramid.view import view_defaults, view_config
from altair.app.ticketing.fanstatic import with_bootstrap
from .api import get_communicator
from ..communication.models import InfoKubunEnum

@view_defaults(decorator=with_bootstrap)
class FamiPortTopView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='top', renderer='top.mako')
    def top(self):
        return dict()


@view_defaults(decorator=with_bootstrap)
class FamiPortServiceView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='service.index', renderer='services/index.mako')
    def index(self):
        return dict()


@view_defaults(decorator=with_bootstrap)
class FamiPortReservedView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def client_code(self):
        return u'000000000000000000000000'

    @property
    def store_code(self):
        return u'00000'

    @view_config(route_name='service.reserved', renderer='services/reserved/index.mako')
    def index(self):
        return dict()

    @view_config(route_name='service.reserved.description', renderer='services/reserved/index.mako')
    def index(self):
        comm = get_communicator(self.request)
        comm.fetch_information(
            type=InfoKubunEnum.Reserved.value,
            store_code=self.store_code,
            client_code=self.client_code,
            event_code_1=None,
            event_code_2=None,
            performance_code=None,
            sales_segment_code=None,
            reserve_number=None,
            auth_number=None
            )

        return dict()
