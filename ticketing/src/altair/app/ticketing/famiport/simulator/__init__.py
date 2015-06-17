from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPFound
from altair.sqlahelper import from_settings

def auth_callback(user_id, request):
    client_code = request.session.get('client_code')
    if client_code is None:
        return []
    else:
        return ['client_code_provided']

def setup_mmk_db(config):
    from altair.sqlahelper import get_global_db_session
    from .models import metadata
    from .mmk import MmkSequence
    from .interfaces import IMmkSequence
    session = get_global_db_session(config.registry, 'famiport_mmk')
    config.registry.registerUtility(
        MmkSequence(metadata, session.bind),
        IMmkSequence
        )

def register_template_globals(event):
    from .helpers import Helpers
    h = Helpers(event['request'])
    event.update(h=h)

def main(global_conf, **local_conf):
    settings = dict(global_conf)
    settings.update(local_conf)
    settings['mako.directories'] = 'altair.app.ticketing.famiport.simulator:templates'
    config = Configurator(settings=settings)
    config.set_root_factory('.resources.BaseResource')
    config.set_authentication_policy(SessionAuthenticationPolicy(callback=auth_callback))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_subscriber(register_template_globals, 'pyramid.events.BeforeRender')
    config.include('pyramid_mako')
    config.include('pyramid_fanstatic')
    config.include('altair.httpsession.pyramid')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.sqlahelper')
    config.include(setup_mmk_db)
    config.include('.configuration')
    config.include('.comm')
    config.add_static_view('static', 'altair.app.ticketing.famiport.simulator:static', cache_max_age=3600)
    config.add_forbidden_view(lambda context, request: HTTPFound(request.route_path('select_shop', _query=dict(return_url=request.path))))
    config.add_route('logout',  '/logout')
    config.add_route('select_shop',  '/select_shop')
    config.add_route('top',  '/', factory='.resources.FamiPortResource')
    config.add_route('service.index', '/services', factory='.resources.FamiPortResource')
    config.add_route('service.reserved', '/services/reserved', factory='.resources.FamiPortResource')
    config.add_route('service.reserved.select', '/services/reserved/select', factory='.resources.FamiPortResource')
    config.add_route('service.reserved.description', '/services/reserved/description', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.info1', '/services/reserved/info1', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.entry', '/services/reserved/entry', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.auth_number_entry', '/services/reserved/auth_number', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.info2', '/services/reserved/info2', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.inquiry', '/services/reserved/inquiry', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.privacy_policy_agreement', '/services/reserved/ppa', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.name_entry', '/services/reserved/name', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.tel_entry', '/services/reserved/tel', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.confirmation', '/services/reserved/confirm', factory='.resources.FamiPortServiceResource')
    config.add_route('service.reserved.completion', '/services/reserved/complete', factory='.resources.FamiPortServiceResource')
    config.add_route('pos.index', '/pos', factory='.resources.FamimaPosResource')
    config.add_route('pos.entry', '/pos/entry', factory='.resources.FamimaPosResource')
    config.add_route('pos.ticketing.confirmation', '/pos/ticketing/confirm', factory='.resources.FamimaPosResource')
    config.add_route('pos.ticketing.completion', '/pos/ticketing/complete', factory='.resources.FamimaPosResource')
    config.scan('.views')
    return config.make_wsgi_app()
