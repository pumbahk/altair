from pyramid.config import Configurator
from wsgiref.simple_server import make_server
from pyramid.view import view_config


@view_config(route_name="hello", renderer="preview.html")
def mock(request):
    return {}

if __name__ == '__main__':
    settings = {"mako.directories": ".", 
                "altaircms.layout_directory": "altaircms:templates/front/layout"}
    config = Configurator(settings=settings)
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.set_request_property("altaircms.auth.api.get_allowable_query", "allowable", reify=True)
    config.add_subscriber("altaircms.subscribers.add_renderer_globals", 
                          "pyramid.events.BeforeRender")

    config.add_route("hello", "/*")
    config.include("altaircms.layout")
    config.include("altaircms.front", route_prefix="/front")
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)
    config.scan()
    app = config.make_wsgi_app()

    import sqlalchemy as sa
    import sqlahelper
    engine = sa.create_engine("mysql+pymysql://altaircms:altaircms@localhost/altaircms?charset=utf8")
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)

    print "localhost:6544"
    server = make_server('0.0.0.0', 6544, app)
    server.serve_forever()
