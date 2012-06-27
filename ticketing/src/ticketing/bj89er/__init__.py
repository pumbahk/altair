from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config
import sqlahelper

def main(global_conf, **settings):
    engine = engine_from_config(settings)
    sqlahelper.add_engine(engine)

    my_session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings, session_factory=my_session_factory)
    config.set_root_factory('.resources.Bj89erCartResource')
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_static_view('static', 'ticketing.bj89er:static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_view('.views.IndexView', route_name='index', attr="get", request_method='GET', renderer='1_form.html')
    config.add_view('.views.IndexView', route_name='index', attr="post", request_method='POST', renderer='1_form.html')
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.scan('ticketing.orders.models')
    config.include('ticketing.cart')
    config.include('ticketing.cart.plugins')
    config.scan('ticketing.cart.views')
    return config.make_wsgi_app()
