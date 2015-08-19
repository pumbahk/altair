from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPFound
from altair.sqlahelper import from_settings

def auth_callback(user_id, request):
    from .api import lookup_user_by_id
    user = lookup_user_by_id(request, user_id)
    return user and [user.role]

def register_template_globals(event):
    from altair.viewhelpers import Namespace
    from .helpers import Helpers
    class CombinedNamespace(object):
        def __init__(self, namespaces):
            self.namespaces = namespaces

        def __getattr__(self, k):
            for ns in self.namespaces:
                v = getattr(ns, k, None)
                if v is not None:
                    return v
            return object.__getattr__(self, k)

    h = CombinedNamespace([
        Helpers(event['request']),
        Namespace(event['request']),
        ])
    event.update(h=h)

def setup_preview(config):
    import urllib2
    settings = config.registry.settings
    opener = urllib2.build_opener()
    from ..communication.interfaces import IFamiPortTicketPreviewAPI
    from ..communication.preview import FamiPortTicketPreviewAPI, CachingFamiPortTicketPreviewAPIAdapterFactory
    ticket_preview_api = FamiPortTicketPreviewAPI(opener, settings['altair.famiport.ticket_preview_api.endpoint_url'])
    ticket_preview_cache_region = settings.get('altair.famiport.ticket_preview_api.cache_region')
    if ticket_preview_cache_region is not None:
        config.include('pyramid_dogpile_cache')
        ticket_preview_api = CachingFamiPortTicketPreviewAPIAdapterFactory(ticket_preview_cache_region)(ticket_preview_api)
    config.registry.registerUtility(ticket_preview_api, IFamiPortTicketPreviewAPI)

def main(global_conf, **local_conf):
    settings = dict(global_conf)
    settings.update(local_conf)
    settings['mako.directories'] = '%s:templates' % __name__
    config = Configurator(settings=settings)
    config.set_root_factory('.resources.BaseResource')
    config.set_authentication_policy(SessionAuthenticationPolicy(callback=auth_callback))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_subscriber(register_template_globals, 'pyramid.events.BeforeRender')
    config.include('pyramid_mako')
    config.include('pyramid_fanstatic')
    config.include('pyramid_dogpile_cache')
    config.include('altair.httpsession.pyramid')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.sqlahelper')
    config.include(setup_preview)

    config.add_renderer('csv', '.renderers.CSVRenderer')
    config.add_static_view('static', '%s:static' % __name__, cache_max_age=3600)
    config.add_forbidden_view(lambda context, request: HTTPFound(request.route_path('login', _query=dict(return_url=request.path))))
    config.add_route('logout',  '/logout')
    config.add_route('login',  '/login')
    config.add_route('top',  '/', factory='.resources.TopResource')
    config.add_route('example.page_needs_authentication',  '/.example/page_needs_authentication', factory='.resources.ExampleResource')
    # Search
    # config.add_route('index', '/', factory='.resources.SearchResource')
    config.add_route('search.receipt', '/receipt/search', factory='.resources.SearchResource')
    config.add_route('search.performance', '/performance/search', factory='.resources.SearchResource')
    config.add_route('search.refund_performance', '/refund/performance/search', factory='.resources.SearchResource')
    config.add_route('search.refund_ticket', '/refund/ticket/search', factory='.resources.SearchResource')
    config.add_route('download.refund_ticket', '/refund/ticket/download', factory='.resources.SearchResource')
    # Detail
    config.add_route('receipt.detail',  '/receipt/{receipt_id}/show', factory='.resources.ReceiptDetailResource')
    config.add_route('performance.detail', '/performance/{performance_id}/show', factory='.resources.PerformanceDetailResource')
    config.add_route('refund_performance.detail',  '/refund/performance/{performance_id}/entry/{refund_entry_id}', factory='.resources.RefundPerformanceDetailResource')
    # Rebook or reprint
    config.add_route('rebook_order', '/receipt/{receipt_id}/rebook_order/{action}', factory='.resources.RebookReceiptResource') # action = (show, rebook, reprint)
    config.add_route('receipt.ticket.info', '/receipt/{receipt_id}/ticket', factory='.resources.APIResource')
    config.add_route('receipt.ticket.render', '/receipt/{receipt_id}/ticket/page{page}', factory='.resources.APIResource')
    config.include('..subscribers')
    config.scan('.views')
    return config.make_wsgi_app()
