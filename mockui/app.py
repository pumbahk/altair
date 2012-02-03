from pyramid.view import view_config
from pyramid.config import Configurator
from paste.httpserver import serve
from pyramid.response import Response
from pyramid.view import render_view_to_response

@view_config(name="foo")
def foo_view(request):
    # returning a response here, in lieu of having
    # declared a renderer to delegate to...
    return Response('Where am i? `{0[whereami]}'.format({"whereami" : "foo!"}))

@view_config(route_name="barbar")
def bar_view(request):
    # handles the response if bar_view has a renderer 
    return render_view_to_response(None, request, name='foo')

@view_config(name="baz")
def baz_view(request):
    # presumably this would not work if foo_view was
    # not returning a Response object directly, as it
    # skips over the rendering part. I think you would
    # have to declare a renderer on this view in that case.
    return foo_view(request)

if __name__ == '__main__':
    config = Configurator()
    # config.add_route("foofoo", "/foo")
    config.add_route("barbar", "/bar")
    config.scan()
    app = config.make_wsgi_app()
    serve(app, host='127.0.0.1', port='5000')
