from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sqlahelper

from altaircms.models import Base

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.get_session().remove()
    sqlahelper.set_base(Base)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)

    config.include("altaircms.plugins")
    config.include("altairsite.front")
    config.include("altairsite.rakuten_auth")

    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.add_static_view('plugins/static', 'altaircms:plugins/static', cache_max_age=3600)
    config.add_static_view("staticasset", "altaircms:../../data/assets", cache_max_age=3600)

    config.add_route('top', '/')
    config.add_view('altairsite.rakuten_auth.index', route_name="top")
    config.add_route('signout', '/signout')
    config.add_view('altairsite.rakuten_auth.signout', route_name='signout')
    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')

    config.add_route('front', '/{page_name:.*}', factory=".front.resources.PageRenderingResource") # fix-url after. implemnt preview
    
    config.add_subscriber(".subscribers.add_renderer_globals", 
                          "pyramid.events.BeforeRender")
    return config.make_wsgi_app()

