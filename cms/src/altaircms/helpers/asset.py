import logging
# def to_show_page(request, asset, filepath=None):
#     if filepath is None:
#         query = dict()
#     elif filepath and hasattr(asset, filepath): # for movie, flash
#         query = dict(filepath=filepath)
#     else:
#         raise Exception("invalid filepath %s" % filepath)
#     return request.route_path("asset_display", asset_id=asset.id, _query=query)

## fixme
_NOT_FOUND_IMG = "/static/img/not_found.jpg"
def to_show_page(request, asset, filepath=None):
    try:
        if filepath is None:
            return request.route_path("__staticasset/", subpath=asset.filepath)
        elif filepath and hasattr(asset, filepath): # for movie, flash
            return request.route_path("__staticasset/", subpath=filepath)
    except KeyError, e:
        logging.debug(e)
        return _NOT_FOUND_IMG

def not_found_image(request): #fixme
    return '<img src="%s" alt="notfound"/>' % _NOT_FOUND_IMG
