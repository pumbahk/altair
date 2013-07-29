import json
import isodate
import urllib
import urllib2
from altair.app.ticketing.core.api import get_organization
from zope.interface import implementer
from altair.app.ticketing.api.impl import CMSCommunicationApi
from .interfaces import IAccessKeyGetter
from altair.preview.data import AccesskeyPermissionData
import logging
logger = logging.getLogger(__name__)
from altair.preview.api import get_preview_secret

@implementer(IAccessKeyGetter)
class CMSAccessKeyGetter(object):
    @classmethod
    def from_settings(cls, settings, prefix="altair.cms.whattime."):
        return cls()

    def __call__(self, request, k):
        api = CMSCommunicationApi.get_instance(request)
        organization = get_organization(request)
        params = {"accesskey": k}
        params.update(organization.get_cms_data()) #id, source
        try:
            res = api.create_response("/auth/api/accesskey/info?{qs}".format(qs=urllib.urlencode(params)))
        except urllib2.HTTPError as e:
            logger.warn(str(e))
            return None

        ## todo: robustness. #slackoff
        data = json.load(res)
        if not data:
            logger.warn("data is empty. url={url}".format(url=res.url))
            return None
        if data["expiredate"]:
            data["expiredate"] = isodate.parse_datetime(data["expiredate"])
        secret = get_preview_secret(request)(k)
        AccesskeyPermissionData.create_from_dict(data, secret=secret).dump(request)
        return data

from altair.app.ticketing.carturl.api import get_cart_url_builder
from altair.app.ticketing.core.models import Event

class CandidatesURLDictBuilder(object):
    def __init__(self, request):
        self.request = request
        self.organization =  get_organization(self.request)

    def build_cms_side(self, event_id, backend_event_id):
        api = CMSCommunicationApi.get_instance(self.request)
        organization = self.organization
        params = {"backend_organization_id": unicode(organization.id) if organization else "", 
                  "event_id": unicode(event_id) if event_id else "", 
                  "backend_event_id": unicode(backend_event_id) if backend_event_id else ""}
        try:
            res = api.create_response("/api/event/url_candidates?{qs}".format(qs=urllib.urlencode(params)))
        except urllib2.HTTPError as e:
            logger.warn(str(e))
            return {}
        cms_side = json.load(res)
        if cms_side["status"] == "NG":
            return {}
        return cms_side["data"]

    def build_backend_side(self, event):
        return {
            "urls": {
                "cart": [get_cart_url_builder(self.request).build(self.request, event, organization=self.organization)], 
                }
            }

    def build(self, event_id=None, backend_event_id=None):
        cms_side = self.build_cms_side(event_id, backend_event_id)
        if "backend_event_id" in cms_side:
            backend_event_id = cms_side["backend_event_id"]
        candidates_dict = cms_side.get("urls", {})
        event = Event.query.filter_by(organization_id=self.organization.id, id=backend_event_id).first()
        logger.warn("backend event id = {}".format(backend_event_id))
        if event is None:
            return candidates_dict
        candidates_dict.update(self.build_backend_side(event)["urls"])
        return candidates_dict

