from ..modelmanager.virtualasset import _NOT_FOUND_IMG
from ..modelmanager.interfaces import IRenderingObjectFactory
from altaircms.asset import PROXY_FACTORY_NAME

## fixme
from .base import RawText

def create_show_img(request, asset, align=None):
    if asset is None:
        width_elt = u""
        height_elt = u""
    else:
        width_elt = u"width=%s" % asset.width if asset.width else u""
        height_elt = u"height=%s" % asset.height if asset.height else u""

    align_elt = u"align=%s" % align if align else u""
    src = rendering_object(request, asset).filepath
    content = u"<img src=%s %s %s %s>" % (src, align_elt, width_elt, height_elt)
    return RawText(content)

def rendering_object(request, asset):
    g = request.registry.getUtility
    return g(IRenderingObjectFactory, PROXY_FACTORY_NAME).create(request, asset)

def not_found_image(request): #fixme
    return '<img src="%s" alt="notfound"/>' % _NOT_FOUND_IMG
