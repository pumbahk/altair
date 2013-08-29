from markupsafe import Markup
_DUMMY = "notfound.gif"
import logging
logger = logging.getLogger(__name__)

from zope.interface import Interface
from zope.interface import implementer

class ITrackingImageGenerator(Interface):
    def __call__(request):
        pass

@implementer(ITrackingImageGenerator)
class TrackingImageTagGenerator(object):
    @classmethod
    def from_settings(cls, settings, prefix="tracking.image."):
        prefix = prefix.rstrip(".")
        return cls(settings[prefix+".urlprefix"], 
                   settings.get(prefix+".dummytext", _DUMMY))

    def __init__(self, urlprefix, dummy):
        self.urlprefix = urlprefix.rstrip("/")
        self.dummy = dummy

    def build_url(self, browse_id):
        return u"{prefix}/{browse_id}.gif".format(prefix=self.urlprefix, browse_id=browse_id)

    def __call__(self, request):
        browse_id = get_tracking_id(request, dummy=self.dummy)
        url = self.build_url(browse_id)
        return Markup(u'<img src="{url}"/>'.format(url=url))

def get_tracking_id(request, dummy=_DUMMY):
    return request.headers.get("X-Altair-Browserid", dummy)

def get_tracking_image(request):
    gen = request.registry.getUtility(ITrackingImageGenerator)
    try:
        if gen:
            return gen(request)
    except Exception as e:
        logger.error(repr(e))
        return ""
    logger.warn("image generator is not found")
    return ""
