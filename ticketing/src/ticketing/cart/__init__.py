from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sqlahelper

import logging

logger = logging.getLogger(__name__)

def includeme(config):
    config.add_route('cart.index', '/events/{event_id}')
    config.add_route('cart.seat_types', 'events/{event_id}/performances/{performance_id}/seat_types')
    config.add_route('cart.products', 'events/{event_id}/performances/{performance_id}/seat_types/{seat_type_id}/products')
    config.add_route('cart.order', 'order')
    config.add_route('cart.payment', 'payment')
    config.add_route('cart.payment.method', 'payment/{payment_method}')

    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')

def main(global_config, **settings):
    engine = engine_from_config(settings)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.set_root_factory('.resources.TicketingCartResrouce')
    config.registry['sa.engine'] = engine
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'ticketing.renderers.csv_renderer_factory')
    config.add_static_view('img', 'ticketing.cart:static', cache_max_age=3600)

    config.include('.')
    config.scan()
    config.scan('..orders.models')

    return config.make_wsgi_app()
