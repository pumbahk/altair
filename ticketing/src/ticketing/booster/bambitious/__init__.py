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
    config.add_booster_settings(settings, prefix="bambitious.")
    config.set_root_factory('.resources.BjBambitiousCartResource')

    config.include("pyramid_layout")
    config.add_layout(".layout.Layout", "ticketing.booster.bambitious:templates/base.html") #xxx:
    config.add_panel("ticketing.booster.panels.input_form", "input_form", renderer="ticketing.booster.bambitious:templates/carts/_form.html")
    config.add_panel("ticketing.booster.panels.input_form", "mobile_input_form", renderer="ticketing.booster.bambitious:templates/carts_mobile/_form.html")
    config.add_panel("ticketing.booster.panels.review_additional_messages", "review.additional_messags", renderer="ticketing.booster.bambitious:templates/order_review/_additional_messages.html")
    config.add_panel("ticketing.booster.panels.review_additional_messages", "review_mobile.additional_messags", renderer="ticketing.booster.bambitious:templates/order_review_mobile/_additional_messages.html")
    config.add_panel("ticketing.booster.panels.complete_notice", "complete_notice", renderer="ticketing.booster.bambitious:templates/carts/_complete_notice.html")    
    config.add_panel("ticketing.booster.panels.complete_notice", "mobile_complete_notice", renderer="ticketing.booster.bambitious:templates/carts_mobile/_complete_notice.html")    

    from ..persistent_profile import PersistentProfileFactory as Default
    class PersistentProfileFactory(Default):
        attr_names = Default.attr_names[:]
        attr_names.extend([
                u't_shirts_size',
                u'product_delivery_method_name', 
                ])
        assert len(set(attr_names)) == len(attr_names)
    ppf = PersistentProfileFactory()
    config.add_persistent_profile_factory(ppf)

def setup_order_product_attribute_metadata(config):
    from ticketing.orders.api import get_metadata_provider_registry
    from .metadata import metadata_provider
    get_metadata_provider_registry(config.registry).registerProvider(metadata_provider)
    
def includeme(config):
    config.include(setup_order_product_attribute_metadata)

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
    config.include("ticketing.booster")

    config.add_subscriber('..subscribers.add_helpers', 'pyramid.events.BeforeRender')
    config.include("ticketing.mails")
    config.add_subscriber('..sendmail.on_order_completed', 'ticketing.cart.events.OrderCompleted')
    return config.make_wsgi_app()
