from pyramid.view import view_config
from pyramid.response import Response

# @view_config(route_name="sample::image_widget", renderer="/sample/widget/image.mak")
# def image_widget(request):
#     image_assets = request.context.get_image_asset_query()
#     return {"image_assets": image_assets}

# @view_config(route_name="sample::freetext_widget", renderer="/sample/widget/freetext.mak")
# def freetext_widget(request):
#     return {}

# @view_config(name="dummy_widget")
# def dummy_widget(request):
#     return Response("dummy")
