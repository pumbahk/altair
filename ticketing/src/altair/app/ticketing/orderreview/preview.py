# encoding: utf-8
from zope.interface import implementer
from altair.now import has_session_key, get_now
from altair.app.ticketing.operators.models import Operator
from altair.preview.api import get_rendered_target
from altair.preview.redirect import Failure
from altair.preview.interfaces import IPreviewPermission
from altair.preview.data import load_preview_permission, PermissionDataNotFound

@implementer(IPreviewPermission)
class OrderReviewPreviewPermission(object):
    def can_preview(self, request):
        return has_session_key(request)

    def has_permission(self, request):
        try:
            data = load_preview_permission(request)
            if not data.verify(request): ##salt+key == secret
                return False
            if data["type"] == "accesskey":
                return self.has_permission_accesskey(request, data)
            else:
                return self.has_permission_operator(request, data)
        except  PermissionDataNotFound:
            return False

    def has_permission_operator(self, request, data):
        operator_id = data.get("operator_id")
        if operator_id is None:
            return Failure(u"ログインユーザの認証キー文字列がセッションから取得できません")
        operator = Operator.query.filter_by(id=request.session["operator_id"]).first()
        if operator is None:
            return Failure(u"ログインユーザーを取得できませんでした")
        organization = request.organization

        if operator.organization_id != organization.id:
            return Failure(u"ログインユーザーのOrganization.idが異なっています({id_0} != {id_1})".format(id_0=organization.id, id_1=operator.organization_id))
        return True

    def has_permission_accesskey(self, request, data):
        expire_at = data.get("expire_at")
        if expire_at and expire_at < get_now(request):
            return Failure(u"取得した認証キーは期限切れです。期限:{expire_at}".format(expire_at=expire_at)) 
        scope = data.get("scope")
        if not scope in ("both", "cart", "onepage+cart"):
            return Failure(u"取得した認証キーのスコープが足りません scope={scope}".format(scope=scope))
        if scope == "onepage+cart":
            target = get_rendered_target(request)
            if target and data["backend_event_id"] != target.target.id:
                return Failure(u"取得した認証キーの閲覧可能なイベントは「{title}」のみです。".format(title=target.target.title))
        return True

def includeme(config):
    config.include("altair.preview")
    config.registry.registerUtility(OrderReviewPreviewPermission(), IPreviewPermission)
    config.add_tween('altair.preview.tweens.preview_tween', under="altair.mobile.tweens.mobile_encoding_convert_factory")
