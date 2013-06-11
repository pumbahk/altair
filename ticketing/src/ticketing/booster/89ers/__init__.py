from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
import json
from pyramid.interfaces import IDict
from sqlalchemy import engine_from_config
import sqlahelper

def setup_booster_settings(config):
    settings = config.registry.settings
    ## register booster settings
    config.include("..config")
    config.add_booster_settings(settings, prefix="89ers.")
    config.set_root_factory('.resources.Bj89ersCartResource')
    
    config.include("pyramid_layout")
    config.add_layout(".layout.Layout", "ticketing.booster.89ers:templates/base.html") #xxx:
    config.add_panel("ticketing.booster.panels.input_form", "input_form", renderer="ticketing.booster.89ers:templates/carts/_form.html")
    config.add_panel("ticketing.booster.panels.input_form", "mobile_input_form", renderer="ticketing.booster.89ers:templates/carts_mobile/_form.html")

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
    config.add_static_view('static', 'ticketing.booster.89ers:static', cache_max_age=3600)
    config.add_static_view('static_', 'ticketing.cart:static', cache_max_age=3600)

    ### selectable renderer
    config.include("ticketing.cart.selectable_renderer")
    domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
    config.registry.utilities.register([], IDict, "altair.cart.domain.mapping", domain_candidates)

    config.include(setup_booster_settings)
    config.include("ticketing.booster")

    config.add_subscriber('..subscribers.add_helpers', 'pyramid.events.BeforeRender')
    config.add_subscriber('..sendmail.on_order_completed', 'ticketing.cart.events.OrderCompleted')
    return config.make_wsgi_app()
