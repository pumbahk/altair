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

default = object()
def to_show_page(request, asset, filepath=default):
    if asset:
        try:
            if filepath is default:
                return request.route_path("__staticasset/", subpath=asset.filepath)                
            filepath = filepath or asset.image_path or _NOT_FOUND_IMG
            if not filepath.startswith("/"):
                return request.route_path("__staticasset/", subpath=filepath)
            else:
                return filepath
        except KeyError, e:
            logging.debug(e)
    return _NOT_FOUND_IMG

def not_found_image(request): #fixme
    return '<img src="%s" alt="notfound"/>' % _NOT_FOUND_IMG
