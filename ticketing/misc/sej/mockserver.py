from pyramid.config import Configurator
from wsgiref.simple_server import make_server
from pyramid.view import view_config
from pyramid.response import FileResponse


@view_config(route_name="hello")
def mock(request):
    print request.url
    print request.POST
    print request.POST["ptct"].file.read()
    path = "./answer.png"
    return FileResponse(path, request=request, cache_max_age=3600)
 
if __name__ == '__main__':
    settings = {}
    config = Configurator(settings=settings)
    config.add_route("hello", "/*")
    config.scan()
    app = config.make_wsgi_app()
    print "localhost:4567"
    server = make_server('0.0.0.0', 4567, app)
    server.serve_forever()
