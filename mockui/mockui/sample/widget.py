from pyramid.view import view_config
from pyramid.response import Response

@view_config(name="image_widget", renderer="/sample/widget/image.mak")
def image_widget(request):
    return {}

@view_config(name="dummy_widget")
def dummy_widget(request):
    return Response("dummy")
