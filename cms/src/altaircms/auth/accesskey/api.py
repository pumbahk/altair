from .control import AccessKeyControl
from .control import PageAccessor
from .control import EventAccessor
from ..models import PageAccesskey

def get_page_access_key_control(request, page):
    return AccessKeyControl(page, PageAccessor, request=request)

def get_event_access_key_control(request, event):
    return AccessKeyControl(event, EventAccessor, request=request)

def dict_from_accesskey_string(request, accesskey_string, organization_id):
    key = PageAccesskey.query.filter_by(hashkey=accesskey_string, organization_id=organization_id).first()
    if key is None:
        return {}
    return {"id": key.id, "accesskey": key.hashkey, "scope": key.scope, "expiredate": key.expiredate.isoformat() if key.expiredate else None, 
            "event_id": key.event_id, "backend_event_id": key.event.backend_id}
