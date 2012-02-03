from pyramid.config import Configurator
from mockui.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)

    config.include("mockui.sample")
    config.include("pyramid_fanstatic")
    config.add_route("home", "/")

    ## fix me:
    config.add_static_view(name='static', path='mockui:static', cache_max_age=3600)
    # config.add_static_view(name='static/css', path='mockui:static/css', cache_max_age=3600)
    config.scan()
    return config.make_wsgi_app()
