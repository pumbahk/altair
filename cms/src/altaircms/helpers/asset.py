import logging

## fixme
_NOT_FOUND_IMG = "/static/img/not_found.jpg"
from .base import RawText

def create_show_img(request, asset, filepath=None, align=None):
    if asset is None:
        width_elt = u""
        height_elt = u""
    else:
        width_elt = u"width=%s" % asset.width if asset.width else u""
        height_elt = u"height=%s" % asset.height if asset.height else u""

    align_elt = u"align=%s" % align if align else u""
    src = to_show_page(request, asset, filepath)
    content = u"<img src=%s %s %s %s>" % (src, align_elt, width_elt, height_elt)
    return RawText(content)

def to_show_page(request, asset, filepath=None):
    if asset:
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
