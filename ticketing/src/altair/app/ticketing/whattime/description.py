# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from altair.preview.data import (
    PermissionDataNotFound, 
    load_preview_permission, 
    AccesskeyPermissionData, 
    OperatorPermissionData
    )

## iter
def description_iterate(request):
    try:
        data = load_preview_permission(request)
        if AccesskeyPermissionData.is_this(data):
            return accesskey_data_iterate(request, data)
        elif OperatorPermissionData.is_this(data):
            return operator_data_iterate(request, data)
        else:
            logger.warn("invalid preview permission type={}".format(data["type"]))
            return []
    except (PermissionDataNotFound, KeyError):
        logger.warn("request.session does not have preview permission")
        return []


def accesskey_data_iterate(request, data):
    L = [
        ("type", u"認証方法"), 
        ("expire_at", u"有効期限"), 
         ("scope", u"スコープ"), 
         ("event_id", u"イベントid(cms)"),  ##
         ("event", u"対象イベント情報"),  ##
         ]
    return [(name, label, data.get(name, u"-")) for name, label in L]

def operator_data_iterate(request, data):
    L = [
        ("type", u"認証方法"), 
        ("expire_at", u"有効期限"), 
         ]
    return [(name, label, data.get(name, u"-")) for name, label in L]
