from zope.interface import implementer
from .interfaces import IRenderingObjectFactory
import urlparse

_NOT_FOUND_IMG = "/static/img/not_found.jpg"

def normalize_url(request, url):
    scheme = request.environ.get("wsgi.url_scheme") or urlparse.urlparse(url).scheme
    return url.replace("s3://", "{0}://s3.amazonaws.com/".format(scheme))

@implementer(IRenderingObjectFactory)
class VirtualAssetFactory(object):
    def __init__(self, static_route_name, notfound_image=_NOT_FOUND_IMG):
        self.static_route_name = static_route_name
        self.notfound_image = notfound_image

    def create(self, request, obj):
        return VirtualAssetModel(request, self, obj)

class VirtualAssetModel(object):
    def __init__(self, request, env, obj):
        self.request = request
        self.env = env
        self.obj = obj

    def route_path(self, subpath):
        subpath = subpath or self.image_path or self.notfound_image
        if subpath.startswith(("/", "http:", "http:")):
            return subpath
        else:
            return self.request.route_path(self.env.static_route_name, subpath=subpath)
        
    @property
    def filepath(self):
        o = self.obj
        if o is None:
            return self.env.notfound_image
        if o.file_url:
            return normalize_url(self.request, o.file_url)
        return self.route_path(o.filepath)

    @property
    def image_path(self):
        o = self.obj
        if o is None:
            return self.env.notfound_image
        if o.image_url:
            return normalize_url(self.request, o.image_url)
        return self.route_path(o.image_path)

    @property
    def thumbnail_path(self):
        o = self.obj
        if o is None:
            return self.env.notfound_image
        if o.thumbnail_url:
            return normalize_url(self.request, o.thumbnail_url)
        return self.route_path(o.thumbnail_path)

    def __getattr__(self, k):
        return getattr(self.obj, k)
