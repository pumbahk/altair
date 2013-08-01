# -*- coding:utf-8 -*-
from zope.interface import implementer
from altair.preview.interfaces import IPreviewPermission
from altair.now import has_session_key
from altaircms.datelib import get_now
from altaircms.page.models import Page
from altaircms.event.models import Event
from altaircms.auth.models import PageAccesskey
import logging
logger = logging.getLogger(__name__)
from altairsite.separation import get_organization_from_request
from .api import get_rendered_target

from altair.preview.redirect import Failure
from altair.preview.data import load_preview_permission, PermissionDataNotFound

@implementer(IPreviewPermission)
class PreviewPermission(object):
    def can_preview(self, request):
        return has_session_key(request)

    def has_permission(self, request):
        try:
            data = load_preview_permission(request)
            status = data.verify(request) ##salt+key == secret
            if not status:
                return status
            if data["type"] == "accesskey":
                return self.has_permission_accesskey(request, data)
            else:
                return self.has_permission_operator(request, data)
        except  PermissionDataNotFound:
            return False

    def has_permission_operator(self, request, data):
        expire_at = data.get("expire_at")
        if expire_at and expire_at < get_now(request):
            return Failure(u"取得したユーザは期限切れです。期限:{expire_at}".format(expire_at=expire_at)) 
        return True

    def has_permission_accesskey(self, request, data):
        key_string = data["accesskey"]
        accesskey = _fetch_accesskey(key_string)
        if accesskey is None:
            return Failure(u"認証キーが取得できません(認証キー文字列={key_string})".format(key_string=key_string))
        organization = get_organization_from_request(request)
        if accesskey.organization_id != organization.id:
            return Failure(u"取得した認証キーとOrganization.idが異なっています({id_0} != {id_1}, 認証キー文字列={key_string})".format(key_string=key_string, id_0=organization.id, id_1=accesskey.organization_id))
        now = get_now(request)
        if accesskey.expiredate and accesskey.expiredate < now:
            return Failure(u"取得した認証キーは期限切れです。期限:{expiredate}".format(expiredate=accesskey.expiredate))
        
        target = get_rendered_target(request)
        if target and accesskey.scope == "onepage": #hmm
            if accesskey.event_id:
                event = _fetch_event(request, accesskey.event_id)
                if target.category == "page" and accesskey.event_id != target.target.event_id:
                    return Failure(u"取得した認証キーのスコープは'onepage'であり、閲覧可能なイベントは「{title}」のみです。".format(title=event.title))
                if target.category == "event" and accesskey.event_id != target.target.id:
                    return Failure(u"取得した認証キーのスコープは'onepage'であり、閲覧可能なイベントは「{title}」のみです。".format(title=event.title))
            elif accesskey.page_id:
                page = _fetch_page(request, accesskey.page_id)
                if target.category == "page" and accesskey.page_id != target.target.id:
                    return Failure(u"取得した認証キーのスコープは'onepage'であり、閲覧可能なイベントは「{title}」のみです。".format(title=page.event.title))
                if target.category == "event" and page and page.event_id != target.target.id:
                    return Failure(u"取得した認証キーのスコープは'onepage'であり、閲覧可能なイベントは「{title}」のみです。".format(title=page.event.title))
        return True

def _fetch_page(request, page_id):
    return request.allowable(Page).filter_by(id=page_id).first()

def _fetch_event(request, event_id):
    return request.allowable(Event).filter_by(id=event_id).first()
        
def _fetch_accesskey(key_string):
    return PageAccesskey.query.filter_by(hashkey=key_string).first()
