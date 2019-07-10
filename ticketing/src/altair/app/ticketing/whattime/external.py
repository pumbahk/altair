# -*- coding:utf-8 -*-
import json
import isodate
import urllib
import urllib2
import logging
from zope.interface import implementer
from altair.app.ticketing.api.impl import CMSCommunicationApi, SiriusCommunicationApi
from altair.app.ticketing.cart import api as cart_api
from altair.preview.data import AccesskeyPermissionData
from altair.preview.api import get_preview_secret
from .interfaces import IAccessKeyGetter

logger = logging.getLogger(__name__)

@implementer(IAccessKeyGetter)
class CMSAccessKeyGetter(object):
    @classmethod
    def from_settings(cls, settings, prefix="altair.cms.whattime."):
        return cls()

    def __call__(self, request, k):
        api = CMSCommunicationApi.get_instance(request)
        organization = cart_api.get_organization(request)
        params = {"accesskey": k}
        params.update(organization.get_cms_data()) #id, source
        is_sirius_api_success = False
        if organization.setting.migrate_to_sirius:
            # Siriusからアクセスキーを取得する。Siriusが安定するまではSirius APIが失敗したら旧CMS APIを実行する
            # Siriusが安定したらSiriusのみに通信するよう修正すること。
            # 本処理ブロックを削除し、communication_apiをSirius向けに生成すれば良い
            sirius_api = SiriusCommunicationApi.get_instance(request)
            try:
                res = sirius_api.create_response("/auth/api/accesskey/info?{qs}".format(qs=urllib.urlencode(params)))
                is_sirius_api_success = True
            except Exception as e:  # Sirius APIが失敗した場合、以降の旧CMS APIのレスポンスを採用
                logger.error('Failed to sirius api access key info: %s', e, exc_info=1)

        if not organization.setting.migrate_to_sirius or not is_sirius_api_success:  # Siriusが安定したら、if条件を外すこと
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

from altair.app.ticketing.carturl.api import get_event_cart_url_builder
from altair.app.ticketing.core.models import Event

class CandidatesURLDictBuilder(object):
    def __init__(self, request):
        self.request = request
        self.organization = cart_api.get_organization(self.request)

    def build_cms_side(self, event_id, backend_event_id):
        api = CMSCommunicationApi.get_instance(self.request)
        organization = self.organization
        params = {"backend_organization_id": unicode(organization.id) if organization else "", 
                  "event_id": unicode(event_id) if event_id else "", 
                  "backend_event_id": unicode(backend_event_id) if backend_event_id else ""}
        is_sirius_api_success = False
        if organization.setting.migrate_to_sirius:
            # SiriusからUserSiteのURLを取得する。Siriusが安定するまではSirius APIが失敗したら旧CMS APIを実行する
            # Siriusが安定したらSiriusのみに通信するよう修正すること。
            # 本処理ブロックを削除し、communication_apiをSirius向けに生成すれば良い
            sirius_api = SiriusCommunicationApi.get_instance(self.request)
            try:
                res = sirius_api.create_response("/api/event/url_candidates?{qs}".format(qs=urllib.urlencode(params)))
                is_sirius_api_success = True
            except Exception as e:  # Sirius APIが失敗した場合、以降の旧CMS APIのレスポンスを採用
                is_sirius_api_success = False

        if not organization.setting.migrate_to_sirius or not is_sirius_api_success:  # Siriusが安定したら、if条件を外すこと
            try:
                res = api.create_response("/api/event/url_candidates?{qs}".format(qs=urllib.urlencode(params)))
            except urllib2.URLError:
                logger.error("connection refused. url=%s",api.get_url("/api/event/url_candidates?{qs}".format(qs=urllib.urlencode(params))))
                return {}
            except urllib2.HTTPError as e:
                logger.error("%s. url=%s", e,api.get_url("/api/event/url_candidates?{qs}".format(qs=urllib.urlencode(params))))
                return {}
        cms_side = json.load(res)
        if cms_side["status"] == "NG":
            return {}
        return cms_side["data"]

    def build_backend_side(self, event):
        return {
            "urls": {
                "cart": [get_event_cart_url_builder(self.request).build(self.request, event, organization=self.organization)], 
                }
            }

    def build(self, event_id=None, backend_event_id=None):
        cms_side = self.build_cms_side(event_id, backend_event_id)
        if "backend_event_id" in cms_side:
            backend_event_id = cms_side["backend_event_id"]
        candidates_dict = cms_side.get("urls", {})
        event = Event.query.filter_by(organization_id=self.organization.id, id=backend_event_id).first()
        logger.info("backend event id = {}".format(backend_event_id))
        if event is None:
            return candidates_dict
        candidates_dict.update(self.build_backend_side(event)["urls"])
        return candidates_dict

