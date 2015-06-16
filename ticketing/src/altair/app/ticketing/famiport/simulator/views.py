# encoding: utf-8
import logging
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from altair.app.ticketing.fanstatic import with_bootstrap
from .api import get_communicator, get_client_configuration_registry
from ..communication.models import InfoKubunEnum, ResultCodeEnum, InformationResultCodeEnum

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamiPortTopView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='top', renderer='top.mako')
    def top(self):
        return dict()


@view_defaults(decorator=with_bootstrap, route_name='select_shop', renderer='select_shop.mako')
class FamiPortSelectShopView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        return dict(store_code=u'', return_url=self.request.params.get('return_url'))

    @view_config(request_method='POST')
    def post(self):
        store_code = self.request.params['store_code']
        return_url = self.request.params.get('return_url')
        if return_url is None:
            return_url = self.request.route_path('top')
        remember(self.request, store_code)
        return HTTPFound(return_url)


@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamiPortServiceView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='service.index', renderer='services/index.mako')
    def index(self):
        return dict()


@view_defaults(decorator=with_bootstrap, permission='authenticated')
class FamiPortReservedServiceSelectionView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='service.reserved', renderer='services/reserved/index.mako')
    def index(self):
        client_configuration_registry = get_client_configuration_registry(self.request)
        return dict(clients=list(client_configuration_registry))

    @view_config(route_name='service.reserved.select')
    def select_service(self):
        client_configuration_registry = get_client_configuration_registry(self.request)
        client = client_configuration_registry.lookup(self.request.params['client_code'])
        if client is not None:
            self.request.session['client_code'] = client.code
            return HTTPFound(self.request.route_path('service.reserved.description'))
        return HTTPFound(self.request.route_path('service.reserved'))


@view_defaults(decorator=with_bootstrap, permission='client_code_provided')
class FamiPortReservedView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def client_configuration(self):
        return client_configuration

    @view_config(route_name='service.reserved.description', renderer='services/reserved/description.mako')
    def index(self):
        comm = get_communicator(self.request)
        result = comm.fetch_information(
            type=InfoKubunEnum.Reserved.value,
            store_code=self.context.store_code,
            client_code=self.context.client_code,
            event_code_1=None,
            event_code_2=None,
            performance_code=None,
            sales_segment_code=None,
            reserve_number=None,
            auth_number=None
            )
        message = '???'
        continuable = False
        if result['resultCode'] == InformationResultCodeEnum.NoInformation.value:
            message = None
            continuable = True
        elif result['resultCode'] == InformationResultCodeEnum.WithInformation.value:
            message = result['infoMessage']
            continuable = True
        elif result['resultCode'] == InformationResultCodeEnum.ServiceUnavailable.value:
            message = u'(service unavailable)'
        elif result['resultCode'] == InformationResultCodeEnum.OtherError.value:
            message = u'(other error) %s' % result.get('infoMessage', u'-')
            continuable = True
        return dict(message=message, continuable=continuable)

