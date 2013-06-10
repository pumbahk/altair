from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
import json
from pyramid.interfaces import IDict
from sqlalchemy import engine_from_config
import sqlahelper


def setup_views(config):
    config.add_route('index', '/')
    config.add_route('contact', '/contact')
    config.add_route('notready', '/notready')

    config.add_view('.views.IndexView', attr='notready', route_name='notready', renderer='carts/notready.html')
    config.add_view('.views.IndexView', attr='notready', request_type='altair.mobile.interfaces.IMobileRequest', route_name='notready', renderer='carts_mobile/notready.html')
    config.add_view('.views.IndexView', route_name='index', attr="get", request_method='GET', renderer='carts/form.html')
    config.add_view('.views.IndexView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='index', 
                    attr="get", request_method='GET', renderer='carts_mobile/form.html')

    config.add_view('.views.IndexView', route_name='index', attr="post", request_method='POST', renderer='carts/form.html')
    config.add_view('.views.IndexView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='index', 
                    attr="post", request_method='POST', renderer='carts_mobile/form.html')

def setup_booster_settings(config):
    settings = config.registry.settings
    ## register booster settings
    config.include("..config")
    config.add_booster_settings(settings, prefix="bambitious.")
    config.set_root_factory('..resources.BoosterCartResource')
    
    config.add_simple_layout(".layout.Layout")

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    my_session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings, session_factory=my_session_factory)

    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')
    config.add_static_view('static', 'ticketing.booster.bambitious:static', cache_max_age=3600)
    config.add_static_view('static_', 'ticketing.cart:static', cache_max_age=3600)

    ### selectable renderer
    config.include("ticketing.cart.selectable_renderer")
    domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
    config.registry.utilities.register([], IDict, "altair.cart.domain.mapping", domain_candidates)

    config.include(setup_booster_settings)
    config.include("..setup_cart")
    config.include('altair.mobile')
    config.include(setup_views)
    config.include("..setup_excviews")
    config.include("..setup_plugins_views")


    config.add_subscriber('..subscribers.add_helpers', 'pyramid.events.BeforeRender')
    return config.make_wsgi_app()
